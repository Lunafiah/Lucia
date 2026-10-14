import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
fixtures = json.load(open('tests/evaluation/language_realization/semantic_graph_preservation/fixtures/audit_fixtures.json', encoding='utf-8'))
import llama_cpp
llm = llama_cpp.Llama('models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf', n_gpu_layers=0, verbose=False)

for i in [0, 3, 5, 7, 36, 37]:
    fix = fixtures[i]
    caps = fix.get('caps_result', {})
    graph = fix.get('authoritative_semantic_graph', {})
    act = caps.get('act', 'ASSERT')
    epistemic = caps.get('epistemic', {}).get('status', 'FACT')
    polarity = caps.get('polarity', True)
    pol_str = 'POS' if polarity else 'NEG (DO_NOT_AFFIRM)'
    pred = caps.get('target_predicate', '')
    focus = caps.get('focus_argument', '')
    nodes = graph.get('nodes', [])
    scopes = graph.get('scopes', [])
    arg0, arg1, arg2 = None, None, None
    for n in nodes:
        role = n.get('role', '')
        if role == ':ARG0': arg0 = n.get('id')
        elif role == ':ARG1': arg1 = n.get('id')
        elif role == ':ARG2': arg2 = n.get('id')
    if not arg0 and focus: arg0 = focus
    lines = ['[REALIZATION CONTRACT]', f'ACT: {act} | POLARITY: {pol_str} | EPISTEMIC: {epistemic}']
    pl = f'EVENT: {pred}'
    if arg0: pl += f' | ARG0: {arg0}'
    if arg1: pl += f' | ARG1: {arg1}'
    if arg2: pl += f' | ARG2: {arg2}'
    lines.append(pl)
    sc = 'ROOT'
    if any(s.get('scope_type') == 'MODAL' for s in scopes): sc = 'MODAL_EMBEDDING'
    elif any(s.get('scope_type') == 'NEGATION' for s in scopes): sc = 'NEGATION_SCOPE'
    prov = caps.get('provenance', {}).get('origin', 'OBSERVATION')
    lines.append(f'SCOPE: {sc} | PROV: {prov}')
    c = []
    if not polarity: c.append('MUST state event NOT occurred/done. NEVER affirm.')
    if act == 'REFUSE': c.append('Refuse ungrounded query. DO NOT speculate.')
    elif act == 'CLARIFY': c.append('Ask clarification question. DO NOT choose.')
    elif epistemic == 'INFERRED': c.append('Hedged claim (seems/appears). NO certainty.')
    if arg0 and arg1 and 'argument_roles' in fix.get('semantic_features', []):
        c.append(f'STRICT ROLES: {arg0} acted on {arg1}. DO NOT reverse.')
    if c:
        lines.append('CONSTRAINT: ' + ' '.join(c))
    contract_txt = '\n'.join(lines)
    toks = llm.tokenize(contract_txt.encode('utf-8'))
    print(f"Fixture {fix['id']}: {len(toks)} tokens")
    print(contract_txt)
    print('-'*50)
