from flask import Flask, request, jsonify, render_template_string
import threading, json

app = Flask(__name__)

# simple HTML page with sliders for mu/sigma for bandwidth/jitter/final_delay
HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Emulator Control</title>
</head>
<body>
  <h3>Emulator Control Panel</h3>
  <form id="form">
    <label>Stochastic enabled: <input type="checkbox" id="stochastic" checked></label><br>
    <h4>Bandwidth (bps)</h4>
    Mean: <input type="range" id="bw_mu" min="1000" max="20000000" step="1000" value="5000000" oninput="updateLabel('lbw_mu', this.value)"><span id="lbw_mu">5000000</span><br>
    Sigma: <input type="range" id="bw_sigma" min="0" max="10000000" step="1000" value="500000"><span id="lbw_sigma">500000</span><br>

    <h4>Final delay (ms)</h4>
    Mean: <input type="range" id="fd_mu" min="0" max="2000" step="1" value="100"><span id="lfd_mu">100</span><br>
    Sigma: <input type="range" id="fd_sigma" min="0" max="1000" step="1" value="20"><span id="lfd_sigma">20</span><br>

    <h4>Jitter (ms)</h4>
    Mean: <input type="range" id="jit_mu" min="0" max="500" step="1" value="0"><span id="ljit_mu">0</span><br>
    Sigma: <input type="range" id="jit_sigma" min="0" max="500" step="1" value="5"><span id="ljit_sigma">5</span><br>

    <button type="button" onclick="apply()">Apply</button>
  </form>

<script>
function updateLabel(id, v){ document.getElementById(id).innerText = v; }
function apply(){
  const body = {
    stochastic_enabled: document.getElementById('stochastic').checked,
    bandwidth_mu: Number(document.getElementById('bw_mu').value),
    bandwidth_sigma: Number(document.getElementById('bw_sigma').value),
    final_delay_mu: Number(document.getElementById('fd_mu').value),
    final_delay_sigma: Number(document.getElementById('fd_sigma').value),
    jitter_mu: Number(document.getElementById('jit_mu').value),
    jitter_sigma: Number(document.getElementById('jit_sigma').value)
  };
  fetch('/update', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)}).then(r=>r.json()).then(j=>alert('Applied: '+JSON.stringify(j)));
}
</script>
</body>
</html>
"""

# shared runtime config (will be modified by UI)
_runtime_config = {}

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json() or {}
    # save keys to runtime config file for server to pick up or in-memory
    # write to a small json file 'runtime_config.json' in project root
    with open('runtime_config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return jsonify(success=True, updated=data)

def run(host='0.0.0.0', port=5001):
    # run flask app (blocking); intended to be launched in a separate thread
    app.run(host=host, port=port)
