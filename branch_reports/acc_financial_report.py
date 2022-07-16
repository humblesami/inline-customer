# -*- coding: utf-8 -*-
from odoo import models
from collections import defaultdict
branch_prefix = 'Br = '


class FinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _compute_amls_results(self, options_list, calling_financial_report=None, sign=1, line_type=None):
        branching = self.env.context.get('branching_for_exp')
        if not branching:
            res = super(FinancialReportLine, self)._compute_amls_results(options_list, calling_financial_report=calling_financial_report, sign=sign)
            return res
        self.ensure_one()
        params = []
        queries = []

        account_financial_report_html = self.financial_report_id
        horizontal_group_by_list = account_financial_report_html._get_options_groupby_fields(options_list[0])
        group_by_list = [self.groupby] + horizontal_group_by_list
        if branching:
            group_by_list.append('branch_id')
        group_by_clause = ','.join('account_move_line.%s' % gb for gb in group_by_list)
        group_by_field = self.env['account.move.line']._fields[self.groupby]

        ct_query = self.env['res.currency']._get_query_currency_table(options_list[0])
        parent_financial_report = self._get_financial_report()
        for i, options in enumerate(options_list):
            new_options = self._get_options_financial_line(options, calling_financial_report, parent_financial_report)
            line_domain = self._get_domain(new_options, parent_financial_report)

            tables, where_clause, where_params = account_financial_report_html._query_get(new_options, domain=line_domain)
            query2 = '''SELECT ''' + (group_by_clause and '%s,' % group_by_clause) + ''' %s AS period_index,
            COALESCE(SUM(ROUND(%s * account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
            FROM ''' + f'''{tables} JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
            WHERE {where_clause} ''' + (group_by_clause and 'GROUP BY %s' % group_by_clause)

            queries.append('''
                SELECT
                    ''' + (group_by_clause and '%s,' % group_by_clause) + '''
                    %s AS period_index,
                    COALESCE(SUM(ROUND(%s * account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance
                FROM ''' + tables + '''
                JOIN ''' + ct_query + ''' ON currency_table.company_id = account_move_line.company_id
                WHERE ''' + where_clause + '''
                ''' + (group_by_clause and 'GROUP BY %s' % group_by_clause) + '''
            ''')
            params += [i, sign] + where_params
        results = {}
        account_balance = {}
        account_branches = {}
        distinct_branches = {}

        parent_financial_report._cr_execute(options_list[0], ' UNION ALL '.join(queries), params)
        rows = self._cr.dictfetchall()
        for res in rows:
            # Build the key.
            key = [res['period_index']]
            for gb in horizontal_group_by_list:
                key.append(res[gb])
            key = tuple(key)
            account_id = res[self.groupby]
            if not account_balance.get(account_id):
                account_balance[account_id] = 0
            if res.get('branch_id'):
                distinct_branches[res['branch_id']] = 1
                if not account_branches.get(account_id):
                    account_branches[account_id] = {}
                account_branches[account_id][res['branch_id']] = res['balance']
            else:
                distinct_branches[0] = 1
                if not account_branches.get(account_id):
                    account_branches[account_id] = {}
                account_branches[account_id][0] = res['balance']
            results.setdefault(res[self.groupby], {})
            account_balance[account_id] += res['balance']
            results[res[self.groupby]][key] = account_balance[account_id]

        branch_ids = tuple(distinct_branches.keys())
        branch_records = self.env['res.branch'].search([('id', 'in', branch_ids)])
        branch_values = branch_records.name_get()
        if distinct_branches.get(0):
            branch_values = [(0, 'None')] + branch_values
        branches_dict = {x[0]: x[1] for x in branch_values}

        if group_by_field.relational:
            sorted_records = self.env[group_by_field.comodel_name].search([('id', 'in', tuple(results.keys()))])
            sorted_values = sorted_records.name_get()
        else:
            sorted_values = [(v, v) for v in sorted(list(results.keys()))]
        ar = []
        for groupby_key, display_name in sorted_values:
            ar.append((groupby_key, display_name, results[groupby_key]))
            acc_branches = account_branches.get(groupby_key)
            acc_branch_ids = list(acc_branches.keys())
            if len(acc_branch_ids) > 1 or acc_branch_ids[0] != 0:
                for bid in acc_branches:
                    vl = {(0,): acc_branches[bid]}
                    ar.append((groupby_key, branch_prefix + branches_dict[bid], vl))
        return ar


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def _create_hierarchy(self, lines, options):

        unfold_all = self.env.context.get('print_mode') and len(options.get('unfolded_lines')) == 0 or options.get('unfold_all')

        def add_to_hierarchy(lines, key, level, parent_id, hierarchy):
            val_dict = hierarchy[key]
            unfolded = val_dict['id'] in options.get('unfolded_lines') or unfold_all
            # add the group totals
            lines.append({
                'id': val_dict['id'],
                'name': val_dict['name'],
                'title_hover': val_dict['name'],
                'unfoldable': True,
                'unfolded': unfolded,
                'level': level,
                'parent_id': parent_id,
                'columns': [{'name': self.format_value(c) if isinstance(c, (int, float)) else c, 'no_format_name': c} for c in val_dict['totals']],
                'name_class': 'o_account_report_name_ellipsis top-vertical-align'
            })
            if not self._context.get('print_mode') or unfolded:
                # add every direct child group recursively
                for child in sorted(val_dict['children_codes']):
                    add_to_hierarchy(lines, child, level + 1, val_dict['id'], hierarchy)
                # add all the lines that are in this group but not in one of this group's children groups
                for l in val_dict['lines']:
                    l['level'] = level + 1
                    l['parent_id'] = val_dict['id']
                lines.extend(val_dict['lines'])

        def compute_hierarchy(lines, level, parent_id):
            # put every line in each of its parents (from less global to more global) and compute the totals
            hierarchy = defaultdict(lambda: {'totals': [None] * len(lines[0]['columns']), 'lines': [], 'children_codes': set(), 'name': '', 'parent_id': None, 'id': ''})
            for line in lines:
                account = self.env['account.account'].browse(line.get('account_id', self._get_caret_option_target_id(line.get('id'))))
                codes = self.get_account_codes(account)  # id, name
                for code in codes:
                    hierarchy[code[0]]['id'] = 'hierarchy_' + str(code[0])
                    hierarchy[code[0]]['name'] = code[1]
                    for i, column in enumerate(line['columns']):
                        if (line.get('name') or '').startswith(branch_prefix):
                            continue
                        if 'no_format_name' in column:
                            no_format = column['no_format_name']
                        elif 'no_format' in column:
                            no_format = column['no_format']
                        else:
                            no_format = None
                        if isinstance(no_format, (int, float)):
                            if hierarchy[code[0]]['totals'][i] is None:
                                hierarchy[code[0]]['totals'][i] = no_format
                            else:
                                hierarchy[code[0]]['totals'][i] += no_format
                for code, child in zip(codes[:-1], codes[1:]):
                    hierarchy[code[0]]['children_codes'].add(child[0])
                    hierarchy[child[0]]['parent_id'] = hierarchy[code[0]]['id']
                hierarchy[codes[-1][0]]['lines'] += [line]
            # compute the tree-like structure by starting at the roots (being groups without parents)
            hierarchy_lines = []
            for root in [k for k, v in hierarchy.items() if not v['parent_id']]:
                add_to_hierarchy(hierarchy_lines, root, level, parent_id, hierarchy)
            return hierarchy_lines

        new_lines = []
        account_lines = []
        current_level = 0
        parent_id = 'root'
        for line in lines:
            if not (line.get('caret_options') == 'account.account' or line.get('account_id')):
                # make the hierarchy with the lines we gathered, append it to the new lines and restart the gathering
                if account_lines:
                    new_lines.extend(compute_hierarchy(account_lines, current_level + 1, parent_id))
                account_lines = []
                new_lines.append(line)
                current_level = line['level']
                parent_id = line['id']
            else:
                # gather all the lines we can create a hierarchy on
                account_lines.append(line)
        # do it one last time for the gathered lines remaining
        if account_lines:
            new_lines.extend(compute_hierarchy(account_lines, current_level + 1, parent_id))
        return new_lines


    def get_report_informations(self, options):
        info = super().get_report_informations(options)
        if info['context'].get('branching_for_exp'):
            main_html = info['main_html'].decode()
            script_to_style = '''<script>$('tr.o_account_reports_default_style.o_js_account_report_inner_row span:contains("'''+branch_prefix+'''")').css({"color":"blue","margin-left":"100px"});console.log('waoo');</script>'''
            main_html += script_to_style
            info['main_html'] = bytes(main_html, 'utf-8')
        return info
