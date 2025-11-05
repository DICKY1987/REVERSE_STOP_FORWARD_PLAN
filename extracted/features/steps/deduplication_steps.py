from behave import given, when, then
from deduplicator import detect_duplicate


@given('a new file "{filename}" with content "{content}"')
def step_new_file(context, filename: str, content: str):
    context.file = {
        "file_path": filename,
        "file_hash": hash(content),
        "trace_id": "bdd-test-001"
    }


@given('an existing file "{existing_filename}" with hash "{file_hash}"')
def step_existing_file(context, existing_filename: str, file_hash: str):
    # Simulate an existing file by storing its hash in context
    context.existing_file = {
        "file_path": existing_filename,
        "file_hash": file_hash,
    }


@given('a new file "{filename}" with the same hash "{file_hash}"')
def step_new_file_same_hash(context, filename: str, file_hash: str):
    context.file = {
        "file_path": filename,
        "file_hash": file_hash,
        "trace_id": "bdd-test-002"
    }


@given('a file that takes 60 seconds to process')
def step_slow_file(context):
    # For BDD, we can't easily sleep; simulate by flagging slow processing
    context.file = {
        "file_path": "slow_file.txt",
        "file_hash": "slowhash",
        "trace_id": "bdd-test-003",
        "process_time": 60
    }


@given('the plugin timeout is set to 30 seconds')
def step_set_timeout(context):
    context.plugin_timeout = 30


@when('I run the deduplicator plugin')
def step_run_deduplicator(context):
    context.result = detect_duplicate(context.file)


@when('I run the deduplicator plugin on "{filename}"')
def step_run_deduplicator_on(context, filename: str):
    # Use context.file previously set for this filename
    context.result = detect_duplicate(context.file)


@then('the file should not be marked as duplicate')
def step_not_duplicate(context):
    assert context.result["is_duplicate"] is False


@then('the file should be allowed to proceed')
def step_file_allowed(context):
    assert context.result.get("status", "success") == "success"


@then('the file should be marked as duplicate')
def step_marked_duplicate(context):
    assert context.result["is_duplicate"] is True


@then('the recommended action should be "{action}"')
def step_recommended_action(context, action: str):
    assert context.result.get("action") == action


@then('the duplicate_of field should be "{original}"')
def step_duplicate_of(context, original: str):
    assert context.result.get("duplicate_of") == original


@then('the plugin should timeout gracefully')
def step_plugin_timeout(context):
    assert context.result.get("status") == "error"
    assert "timeout" in context.result.get("error_message", "").lower()


@then('return an error status')
def step_return_error(context):
    assert context.result.get("status") == "error"