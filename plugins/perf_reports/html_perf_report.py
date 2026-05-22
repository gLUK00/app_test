"""Plugin de rapport de performance HTML autonome."""
import json
from datetime import datetime
from plugins.perf_reports.perf_report_base import PerfReportBase


class HTMLPerfReportPlugin(PerfReportBase):
    """Génère un rapport de performance autonome au format HTML avec graphiques intégrés."""

    plugin_name = "html"
    version = "1.0.0"
    author = "TestGyver Team"

    # ------------------------------------------------------------------
    # Métadonnées
    # ------------------------------------------------------------------

    def get_metadata(self):
        return {
            "name": "Rapport HTML",
            "version": self.version,
            "author": self.author,
            "description": "Rapport de performance autonome au format HTML avec tableaux et graphiques (Chart.js embarqué).",
            "output_format": self.get_output_format()
        }

    def validate_config(self, config):
        return (True, "")

    def get_output_format(self):
        return "html"

    def get_configuration_schema(self):
        return [
            {
                "name": "title",
                "type": "string",
                "label": "Titre du rapport",
                "placeholder": "Rapport de tests de performance",
                "required": False
            },
            {
                "name": "include_charts",
                "type": "checkbox",
                "label": "Inclure les graphiques",
                "default": True,
                "required": False
            },
            {
                "name": "theme",
                "type": "select",
                "label": "Thème",
                "options": [
                    {"value": "light", "label": "Clair"},
                    {"value": "dark",  "label": "Sombre"}
                ],
                "required": False
            }
        ]

    # ------------------------------------------------------------------
    # Génération
    # ------------------------------------------------------------------

    def generate(self, perf_rapport, config=None):
        """
        Génère le rapport HTML.

        Args:
            perf_rapport (dict): Document rapport de performance.
            config (dict): Configuration personnalisée.

        Returns:
            dict: {"success": bool, "message": str, "file_path": str}
        """
        try:
            config = config or {}
            output_path = config.get('output_path')
            if not output_path:
                return {"success": False, "message": "output_path manquant dans la configuration"}

            title = config.get('title') or perf_rapport.get('details') or "Rapport de performance"
            include_charts = config.get('include_charts', True)
            theme = config.get('theme', 'light')

            html_content = self._build_html(perf_rapport, title, include_charts, theme)

            with open(output_path, 'w', encoding='utf-8') as fh:
                fh.write(html_content)

            return {
                "success": True,
                "message": "Rapport HTML généré avec succès",
                "file_path": output_path
            }
        except Exception as exc:
            return {"success": False, "message": str(exc), "file_path": None}

    # ------------------------------------------------------------------
    # Construction du HTML
    # ------------------------------------------------------------------

    def _build_html(self, rapport, title, include_charts, theme):
        perf = rapport.get('perf_results') or {}
        tests = perf.get('tests', [])
        config = rapport.get('perf_config') or {}

        # Dates & durée
        date_str = ""
        if rapport.get('dateCreated'):
            dc = rapport['dateCreated']
            if hasattr(dc, 'strftime'):
                date_str = dc.strftime('%d/%m/%Y %H:%M:%S')
            else:
                date_str = str(dc)

        start_ts = rapport.get('startTime')
        end_ts   = rapport.get('endTime')
        if start_ts and end_ts:
            duration_ms = int((end_ts - start_ts) * 1000)
        else:
            duration_ms = rapport.get('executionTimeMs', 0)
        duration_s = duration_ms / 1000 if duration_ms else 0

        # Statistiques globales
        total    = perf.get('total_instances', 0)
        executed = perf.get('executed_instances', 0)
        passed   = perf.get('passed_instances', 0)
        failed   = perf.get('failed_instances', 0)
        rate     = round(passed / executed * 100, 1) if executed > 0 else 0
        avg_ms   = perf.get('exec_time_avg_ms', 0)
        min_ms   = perf.get('exec_time_min_ms', 0) or 0
        max_ms   = perf.get('exec_time_max_ms', 0)

        bg_color   = '#1a1a2e' if theme == 'dark' else '#f8f9fa'
        text_color = '#e0e0e0' if theme == 'dark' else '#212529'
        card_bg    = '#16213e' if theme == 'dark' else '#ffffff'
        border_col = '#0f3460' if theme == 'dark' else '#dee2e6'

        # Données Chart.js sérialisées
        chart_labels  = json.dumps([t.get('name', '?') for t in tests])
        chart_passed  = json.dumps([t.get('passed_instances', 0) for t in tests])
        chart_failed  = json.dumps([t.get('failed_instances', 0) for t in tests])
        chart_avg     = json.dumps([t.get('exec_time_avg_ms', 0) for t in tests])
        chart_min     = json.dumps([t.get('exec_time_min_ms', 0) or 0 for t in tests])
        chart_max     = json.dumps([t.get('exec_time_max_ms', 0) for t in tests])
        chart_rates   = json.dumps([
            round(t.get('passed_instances', 0) / t.get('executed_instances', 1) * 100, 1)
            if t.get('executed_instances', 0) > 0 else 0
            for t in tests
        ])
        chart_rate_colors = json.dumps([
            'rgba(25, 135, 84, 0.8)' if (
                t.get('passed_instances', 0) / t.get('executed_instances', 1) * 100 >= 80
                if t.get('executed_instances', 0) > 0 else False
            ) else (
                'rgba(255, 193, 7, 0.8)' if (
                    t.get('passed_instances', 0) / t.get('executed_instances', 1) * 100 >= 50
                    if t.get('executed_instances', 0) > 0 else False
                ) else 'rgba(220, 53, 69, 0.8)'
            )
            for t in tests
        ])

        # Tableau des tests
        rows_html = ""
        for t in tests:
            t_exec = t.get('executed_instances', 0)
            t_pass = t.get('passed_instances', 0)
            t_fail = t.get('failed_instances', 0)
            t_rate = round(t_pass / t_exec * 100, 1) if t_exec > 0 else 0
            if t_rate >= 80:
                badge_class = "badge-success"
            elif t_rate >= 50:
                badge_class = "badge-warning"
            else:
                badge_class = "badge-danger"
            rows_html += f"""
            <tr>
                <td>{t.get('name', '—')}</td>
                <td class="text-center">{t.get('total_instances', 0)}</td>
                <td class="text-center text-success">{t_pass}</td>
                <td class="text-center text-danger">{t_fail}</td>
                <td class="text-center"><span class="badge {badge_class}">{t_rate}%</span></td>
                <td class="text-right mono">{t.get('exec_time_avg_ms', 0)} ms</td>
                <td class="text-right mono">{t.get('exec_time_min_ms', 0) or 0} ms</td>
                <td class="text-right mono">{t.get('exec_time_max_ms', 0)} ms</td>
                <td class="text-right mono">{t.get('exec_time_total_ms', 0)} ms</td>
            </tr>"""

        # Graphiques (optionnel)
        charts_section = ""
        if include_charts and tests:
            charts_section = f"""
        <div class="section">
            <h2>Graphiques</h2>

            <div class="charts-grid">
                <div class="chart-card">
                    <h3>Instances par test</h3>
                    <canvas id="chartInstances"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Temps de réponse (ms)</h3>
                    <canvas id="chartTime"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Résultat global</h3>
                    <canvas id="chartDoughnut"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Taux de succès par test</h3>
                    <canvas id="chartRate"></canvas>
                </div>
            </div>
        </div>

        <script>
        (function() {{
            const labels = {chart_labels};
            const isDark = {json.dumps(theme == 'dark')};
            Chart.defaults.color = isDark ? '#ccc' : '#444';

            new Chart(document.getElementById('chartInstances'), {{
                type: 'bar',
                data: {{
                    labels,
                    datasets: [
                        {{ label: 'Réussies', data: {chart_passed}, backgroundColor: 'rgba(25,135,84,0.75)' }},
                        {{ label: 'Échouées', data: {chart_failed}, backgroundColor: 'rgba(220,53,69,0.75)' }}
                    ]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});

            new Chart(document.getElementById('chartTime'), {{
                type: 'bar',
                data: {{
                    labels,
                    datasets: [
                        {{ label: 'Moy (ms)', data: {chart_avg}, backgroundColor: 'rgba(13,110,253,0.75)' }},
                        {{ label: 'Min (ms)', data: {chart_min}, backgroundColor: 'rgba(108,117,125,0.5)' }},
                        {{ label: 'Max (ms)', data: {chart_max}, backgroundColor: 'rgba(255,193,7,0.75)' }}
                    ]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});

            new Chart(document.getElementById('chartDoughnut'), {{
                type: 'doughnut',
                data: {{
                    labels: ['Réussies', 'Échouées'],
                    datasets: [{{
                        data: [{passed}, {failed}],
                        backgroundColor: ['rgba(25,135,84,0.8)', 'rgba(220,53,69,0.8)']
                    }}]
                }},
                options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
            }});

            new Chart(document.getElementById('chartRate'), {{
                type: 'bar',
                data: {{
                    labels,
                    datasets: [{{
                        label: 'Taux de succès (%)',
                        data: {chart_rates},
                        backgroundColor: {chart_rate_colors},
                        indexAxis: 'y'
                    }}]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    scales: {{ x: {{ min: 0, max: 100 }} }},
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        }})();
        </script>"""

        # Configuration résumée
        cfg_rows = ""
        cfg_map = {
            'tests_parallel': 'Parallélisme inter-tests',
            'tests_parallel_count': 'Workers inter-tests',
        }
        for k, label in cfg_map.items():
            if k in config:
                cfg_rows += f"<tr><td>{label}</td><td>{config[k]}</td></tr>"

        rate_class = "success" if rate >= 80 else ("warning" if rate >= 50 else "danger")

        return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body   {{ font-family: system-ui, sans-serif; background: {bg_color}; color: {text_color}; padding: 2rem; }}
  h1     {{ font-size: 1.6rem; margin-bottom: 0.25rem; }}
  h2     {{ font-size: 1.2rem; border-bottom: 2px solid {border_col}; padding-bottom: 0.4rem; margin: 2rem 0 1rem; }}
  h3     {{ font-size: 1rem; margin-bottom: 0.75rem; }}
  .meta  {{ color: #888; font-size: 0.85rem; margin-bottom: 1.5rem; }}
  .section {{ margin-bottom: 2rem; }}

  /* KPI cards */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; }}
  .kpi-card {{
    background: {card_bg}; border: 1px solid {border_col};
    border-radius: 8px; padding: 1rem; text-align: center;
  }}
  .kpi-card .value {{ font-size: 2rem; font-weight: 700; }}
  .kpi-card .label {{ font-size: 0.75rem; text-transform: uppercase; color: #888; margin-top: 0.25rem; }}
  .kpi-card.success .value {{ color: #198754; }}
  .kpi-card.danger  .value {{ color: #dc3545; }}
  .kpi-card.warning .value {{ color: #ffc107; }}
  .kpi-card.info    .value {{ color: #0dcaf0; }}
  .kpi-card.primary .value {{ color: #0d6efd; }}

  /* Table */
  table       {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
  thead th    {{ background: {card_bg}; padding: 0.6rem 0.75rem; text-align: left;
                 text-transform: uppercase; font-size: 0.75rem; border-bottom: 2px solid {border_col}; }}
  tbody td    {{ padding: 0.5rem 0.75rem; border-bottom: 1px solid {border_col}; vertical-align: middle; }}
  tbody tr:hover {{ background: {card_bg}; }}
  .text-center {{ text-align: center; }}
  .text-right  {{ text-align: right; }}
  .mono        {{ font-family: monospace; }}
  .text-success {{ color: #198754; }}
  .text-danger  {{ color: #dc3545; }}

  /* Badges */
  .badge         {{ display: inline-block; padding: 0.25em 0.5em; border-radius: 4px;
                    font-size: 0.8rem; font-weight: 600; }}
  .badge-success {{ background: #198754; color: #fff; }}
  .badge-warning {{ background: #ffc107; color: #000; }}
  .badge-danger  {{ background: #dc3545; color: #fff; }}

  /* Charts */
  .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; }}
  .chart-card  {{ background: {card_bg}; border: 1px solid {border_col}; border-radius: 8px; padding: 1rem; }}

  /* Config table */
  .config-table td {{ padding: 0.3rem 0.6rem; border-bottom: 1px solid {border_col}; font-size: 0.85rem; }}
  .config-table td:first-child {{ color: #888; width: 50%; }}

  /* Footer */
  footer {{ margin-top: 3rem; text-align: center; font-size: 0.75rem; color: #666; }}
</style>
</head>
<body>

<header class="section">
  <h1>{title}</h1>
  <p class="meta">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')} &nbsp;|&nbsp; Exécuté le {date_str}</p>
</header>

<div class="section">
  <h2>Résumé global</h2>
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="value">{total}</div>
      <div class="label">Instances totales</div>
    </div>
    <div class="kpi-card success">
      <div class="value">{passed}</div>
      <div class="label">Réussies</div>
    </div>
    <div class="kpi-card danger">
      <div class="value">{failed}</div>
      <div class="label">Échouées</div>
    </div>
    <div class="kpi-card {rate_class}">
      <div class="value">{rate}%</div>
      <div class="label">Taux de succès</div>
    </div>
    <div class="kpi-card info">
      <div class="value">{avg_ms} ms</div>
      <div class="label">Temps moyen</div>
    </div>
    <div class="kpi-card primary">
      <div class="value">{min_ms} ms</div>
      <div class="label">Temps min</div>
    </div>
    <div class="kpi-card warning">
      <div class="value">{max_ms} ms</div>
      <div class="label">Temps max</div>
    </div>
    <div class="kpi-card">
      <div class="value">{duration_s:.1f} s</div>
      <div class="label">Durée totale</div>
    </div>
  </div>
</div>

<div class="section">
  <h2>Résultats par test</h2>
  <div style="overflow-x:auto;">
    <table>
      <thead>
        <tr>
          <th>Test</th>
          <th class="text-center">Total</th>
          <th class="text-center">Réussi</th>
          <th class="text-center">Échoué</th>
          <th class="text-center">Taux</th>
          <th class="text-right">T. moyen</th>
          <th class="text-right">T. min</th>
          <th class="text-right">T. max</th>
          <th class="text-right">T. total</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</div>

{charts_section}

{f'''<div class="section">
  <h2>Configuration</h2>
  <table class="config-table"><tbody>{cfg_rows}</tbody></table>
</div>''' if cfg_rows else ''}

<footer>TestGyver &mdash; Rapport de performance</footer>

</body>
</html>"""
