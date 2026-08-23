from __future__ import annotations
import json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPTS=ROOT/'scripts'; sys.path.insert(0,str(SCRIPTS))
from hooks import dispatch_hooks  # noqa: E402
from state_engine import LatticeError  # noqa: E402

class HookDispatchTest(unittest.TestCase):
    def test_hooks_run_in_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); (root/'runtime').mkdir(); sink=root/'sink.txt'; hook=root/'hook.py'
            hook.write_text("import json,pathlib,sys\nlabel,target=sys.argv[1],pathlib.Path(sys.argv[2])\nevent=json.loads(sys.stdin.read())\nwith target.open('a') as f:f.write(label+':'+event['event_type']+'\\n')\n")
            (root/'runtime'/'hooks.json').write_text(json.dumps({'action_claimed':[[sys.executable,str(hook),'first',str(sink)],[sys.executable,str(hook),'second',str(sink)]]}))
            results=dispatch_hooks(root,'action_claimed',{'event_type':'action_claimed'})
            self.assertEqual([r['returncode'] for r in results],[0,0]); self.assertEqual(sink.read_text(),'first:action_claimed\nsecond:action_claimed\n')
    def test_hook_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); (root/'runtime').mkdir(); (root/'runtime'/'hooks.json').write_text(json.dumps({'policy_checked':[[sys.executable,'-c','import sys;sys.exit(7)']]}))
            with self.assertRaises(LatticeError): dispatch_hooks(root,'policy_checked',{'event_type':'policy_checked'})

if __name__=='__main__': unittest.main()
