"""Tests for Feature 56: Actions Extension."""
import pytest


def test_launch_action_new():
    from oxidize_pdf import LaunchAction

    action = LaunchAction("notepad.exe")
    assert action is not None


def test_launch_action_application():
    from oxidize_pdf import LaunchAction

    action = LaunchAction.application("firefox")
    assert action is not None


def test_launch_action_document():
    from oxidize_pdf import LaunchAction

    action = LaunchAction.document("report.pdf")
    assert action is not None


def test_launch_action_builders():
    from oxidize_pdf import LaunchAction

    action = LaunchAction.application("notepad.exe").with_params("/p").in_new_window(True)
    assert action is not None


def test_standard_named_action_constants():
    from oxidize_pdf import StandardNamedAction

    assert StandardNamedAction.NEXT_PAGE is not None
    assert StandardNamedAction.PREV_PAGE is not None
    assert StandardNamedAction.FIRST_PAGE is not None
    assert StandardNamedAction.LAST_PAGE is not None
    assert StandardNamedAction.GO_BACK is not None
    assert StandardNamedAction.GO_FORWARD is not None
    assert StandardNamedAction.PRINT is not None
    assert StandardNamedAction.SAVE_AS is not None
    assert StandardNamedAction.FULL_SCREEN is not None
    assert StandardNamedAction.FIT_PAGE is not None
    assert StandardNamedAction.FIT_WIDTH is not None


def test_named_action_standard():
    from oxidize_pdf import NamedAction, StandardNamedAction

    action = NamedAction.standard(StandardNamedAction.PRINT)
    assert action is not None
    assert action.name() == "Print"


def test_named_action_custom():
    from oxidize_pdf import NamedAction

    action = NamedAction.custom("MyCustomAction")
    assert action.name() == "MyCustomAction"


def test_named_action_factory_methods():
    from oxidize_pdf import NamedAction

    assert NamedAction.next_page().name() == "NextPage"
    assert NamedAction.prev_page().name() == "PrevPage"
    assert NamedAction.first_page().name() == "FirstPage"
    assert NamedAction.last_page().name() == "LastPage"
    assert NamedAction.print().name() == "Print"
    assert NamedAction.full_screen().name() == "FullScreen"
    assert NamedAction.fit_page().name() == "FitPage"
    assert NamedAction.fit_width().name() == "FitWidth"


def test_submit_form_action_new():
    from oxidize_pdf import SubmitFormAction

    action = SubmitFormAction("https://example.com/submit")
    assert action is not None


def test_submit_form_action_builders():
    from oxidize_pdf import SubmitFormAction

    action = (
        SubmitFormAction("https://example.com/submit")
        .as_html()
        .with_fields(["name", "email"])
        .with_charset("UTF-8")
    )
    assert action is not None


def test_submit_form_action_as_xml():
    from oxidize_pdf import SubmitFormAction

    action = SubmitFormAction("https://example.com/submit").as_xml()
    assert action is not None


def test_submit_form_action_as_pdf():
    from oxidize_pdf import SubmitFormAction

    action = SubmitFormAction("https://example.com/submit").as_pdf()
    assert action is not None


def test_hide_action_new():
    from oxidize_pdf import HideAction

    action = HideAction(["field1", "field2"])
    assert action is not None


def test_hide_action_hide():
    from oxidize_pdf import HideAction

    action = HideAction(["myField"]).hide()
    assert action is not None


def test_hide_action_show():
    from oxidize_pdf import HideAction

    action = HideAction(["myField"]).show()
    assert action is not None


def test_hide_action_single_target():
    from oxidize_pdf import HideAction

    action = HideAction(["singleField"])
    assert action is not None
