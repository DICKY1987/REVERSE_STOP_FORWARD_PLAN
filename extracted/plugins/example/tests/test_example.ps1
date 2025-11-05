Describe "Process-File" {
    Context "Valid Input" {
        It "Should return success status" {
            $input = @{
                FilePath = "test.txt"
                Content = "hello"
                TraceId = "test-001"
            }

            $result = Process-File -InputData $input

            $result.status | Should -Be "success"
            $result.trace_id | Should -Be "test-001"
        }
    }

    Context "Error Handling" {
        It "Should handle missing required fields" {
            $input = @{
                FilePath = "test.txt"
                # Missing Content!
                TraceId = "test-002"
            }

            $result = Process-File -InputData $input

            $result.status | Should -Be "error"
            $result.error_message | Should -Match "content"
        }
    }

    Context "External Dependencies" {
        It "Should call external API correctly" {
            Mock Invoke-ExternalAPI { return @{ api_status = "ok" } }

            $input = @{
                FilePath = "test.txt"
                Content = "data"
                TraceId = "test-003"
            }

            $result = Process-File -InputData $input

            Assert-MockCalled Invoke-ExternalAPI -Times 1
            $result.status | Should -Be "success"
        }
    }
}

# Run: Invoke-Pester -Path plugins/example/tests/