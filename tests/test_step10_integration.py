"""Offline tests for the fail-closed Step 10 integration helper."""
import ast
import unittest
from scripts.prepare_step10_integration import integrate, UnsafeIntegration, NAV

STARTER = '''import streamlit as st
st.set_page_config(page_title="BTA 2.0", layout="wide")
st.markdown("<style>.stApp{color:white}</style>", unsafe_allow_html=True)
sections = ["Home", "NBA", "NFL", "College Football", "My Slip"]
page = st.selectbox("Navigate", sections)
if page == "Home":
    st.subheader("BTA Research Hub")
    st.info("Independent research engine coming next")
elif page == "My Slip":
    st.subheader("My Slip")
    st.info("Saved slips and analysis are coming next.")
else:
    st.subheader(f"{page} Research")
    st.info("Research under development")
'''

class TestStep10Integration(unittest.TestCase):
    def test_compiles(self):
        compile(integrate(STARTER), "candidate.py", "exec")

    def test_imports_once(self):
        result = integrate(STARTER)
        self.assertEqual(result.count("from ui.schedule_sections import"), 1)
        self.assertEqual(result.count("from domain.contracts import Sport"), 1)

    def test_home_wired_once(self):
        self.assertEqual(integrate(STARTER).count("render_home_schedules(days=7"), 1)

    def test_each_sport_wired_once(self):
        result = integrate(STARTER)
        for sport in ("Sport.NBA", "Sport.NFL", "Sport.COLLEGE_FOOTBALL"):
            self.assertEqual(result.count(f"render_sport_schedule({sport},"), 1)

    def test_preserves_my_slip_and_css(self):
        result = integrate(STARTER)
        self.assertIn('st.info("Saved slips and analysis are coming next.")', result)
        self.assertIn(".stApp{color:white}", result)

    def test_preserves_original_section_labels(self):
        result = integrate(STARTER)
        tree = ast.parse(result)
        self.assertTrue(any(isinstance(n, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == "sections" for t in n.targets)
                            and tuple(ast.literal_eval(n.value)) == NAV for n in tree.body))

    def test_second_application_is_blocked(self):
        with self.assertRaises(UnsafeIntegration):
            integrate(integrate(STARTER))

    def test_modified_navigation_fails_closed(self):
        with self.assertRaises(UnsafeIntegration):
            integrate(STARTER.replace('"My Slip"]', '"Model Lab"]'))

    def test_missing_nav_if_fails_closed(self):
        with self.assertRaises(UnsafeIntegration):
            integrate(STARTER.replace('if page == "Home":', 'if page == "Dashboard":'))

    def test_missing_streamlit_import_fails_closed(self):
        with self.assertRaises(UnsafeIntegration):
            integrate(STARTER.replace("import streamlit as st", ""))

    def test_no_catch_all_fails_closed(self):
        source = STARTER.replace('else:\n    st.subheader(f"{page} Research")\n    st.info("Research under development")\n', "")
        with self.assertRaises(UnsafeIntegration):
            integrate(source)

    def test_explicit_branches(self):
        source = STARTER.replace('else:\n    st.subheader(f"{page} Research")\n    st.info("Research under development")',
          'elif page == "NBA":\n    st.subheader("NBA")\nelif page == "NFL":\n    st.subheader("NFL")\nelif page == "College Football":\n    st.subheader("College Football")')
        candidate = integrate(source)
        compile(candidate, "candidate.py", "exec")
        self.assertEqual(candidate.count("render_sport_schedule("), 3)

    def test_sport_fallback_is_nested_under_else(self):
        result = integrate(STARTER)
        fragment = result.split('else:\n    st.subheader(f"{page} Research")', 1)[1]
        self.assertIn('    if page == \'NBA\':', fragment)
        self.assertIn('    elif page == \'NFL\':', fragment)

    def test_other_code_is_preserved(self):
        source = STARTER.replace('st.markdown("<style>', 'st.caption("Hello")\nst.markdown("<style>')
        self.assertIn('st.caption("Hello")', integrate(source))

    def test_no_network_calls_used_in_patcher(self):
        import inspect
        from scripts import prepare_step10_integration as module
        tree = ast.parse(inspect.getsource(module))
        invoked = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(invoked.intersection({"fetch", "urlopen", "requests"}))

if __name__ == "__main__":
    unittest.main()
