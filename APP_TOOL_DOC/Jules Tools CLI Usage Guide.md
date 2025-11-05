

# **Technical Specification Report: Machine-Readable Usage Guide for Jules Tools CLI Integration**

## **I. Strategic Overview: Jules CLI as an AI Toolchain Component**

### **I.1. Introduction and Mandate**

The primary objective of this specification report is to define a non-ambiguous, deterministic interface for integrating the Jules Tools Command Line Interface (CLI) into automated systems, particularly those managed by an AI application designed for task orchestration and automated code remediation. This document transcends simple command documentation by establishing operational constraints, environmental requirements, and failure mitigation strategies derived from an analysis of the existing public documentation. The focus is on structuring the information (via definitive lists and structured analysis) to facilitate seamless, predictable execution by an upstream AI agent.

### **I.2. Installation and Initial Availability**

The Jules CLI is distributed as a Node Package Manager (npm) module. For operational readiness, the tool must be installed globally on the host system where the AI application resides. This is achieved using the command: npm install \-g @google/jules.1 Once the installation process successfully completes, the primary entry point for all interactions becomes the jules command, available directly in the terminal environment.1

The mandatory reliance on a global npm installation dictates a critical architectural requirement for the AI application's host environment. The execution environment running the AI application must have a pre-configured and stable Node.js/npm environment established prior to any attempt to execute Jules commands. This implies a required pre-flight validation check within the AI application’s setup routine to verify the presence of Node.js and the successful installation of the @google/jules package before proceeding with any automation tasks. This rigorous verification minimizes potential failures stemming from prerequisite toolchain deficiencies on the host machine.

### **I.3. Critical Input Requirements for Task Initiation**

Successful task initiation through Jules requires several defined steps within the user interface, which must be programmatically replicated or assumed in an automated workflow. These requirements are predicated on selecting a specific repository from the codebase selector and choosing a target branch (though the default branch is automatically selected if no modification is necessary).2

Crucially, the task initiation process demands the supply of a **clear, specific prompt**.2 Examples of acceptable input include highly targeted instructions, such as: "Add a test for 'parseQueryString function in utils.js".2 The analysis of failure modes strongly reinforces the importance of this requirement, as prompts classified as "vague or overly broad" are listed among the most frequent causes of task failure.3

This constraint elevates the prompt from a simple textual input to a critical configuration parameter. The AI application responsible for initiating Jules tasks must therefore implement a specialized component—a Prompt Specificity Validator (PSV)—mandated to enforce structural rigor in the task description. This structured enforcement is necessary to address a known, primary failure vector at the earliest stage, ensuring that instructions provided to Jules are non-ambiguous and highly targeted towards the desired outcome (e.g., explicitly naming the required action, the target file, and the intended function modification).

## **II. Environmental Specification: The Jules Virtual Machine Host**

Understanding the precise execution environment where Jules operates is mandatory for the AI agent to generate effective setup scripts, manage dependencies, and accurately predict task execution outcomes.

### **II.1. The Jules Execution Environment (Jules VM)**

Every Jules task is executed inside a secure, specialized execution environment: a short-lived **Ubuntu Linux virtual machine (VM)**.5 The "short-lived" nature of the VM is a significant constraint, implying that the environment is non-persistent and likely reset or destroyed between individual tasks initiated by the AI agent.5 This architectural design reinforces the necessity for all setup scripts to be complete, self-contained, and fully idempotent, ensuring that every task starts from a fully prepared state.

For environment configuration, particularly in complex projects, the user or the automated system must provide an explicit setup script. This script is input via the web interface under the repository's **Configuration** section within the **Initial Setup** window.5 For simpler environments, Jules attempts an automatic setup, sometimes drawing guidance from repository files like agents.md or readme.md.5

### **II.2. The Critical Toolchain Index and Compatibility**

To maximize execution efficiency and minimize the necessary complexity of manually written setup scripts, the AI agent must prioritize reliance on the extensive catalog of developer tools preinstalled within the Jules VM. Any setup script generated by the AI should cross-reference required dependencies against this established toolchain index.

Table: Select Preinstalled Tools and Versions in Jules VM

| Tool Category | Tool | Version(s) Available | Source |
| :---- | :---- | :---- | :---- |
| Python | python3, python | 3.12.11 | 5 |
| Python Utilities | pip | 25.1.1 | 5 |
| Python Testing/Linting | pytest, ruff | 8.4.0, 0.12.0 | 5 |
| NodeJS (Default) | node | v22.16.0 | 5 |
| NodeJS (Others) | node | v18.20.8, v20.19.2 | 5 |
| NodeJS Utilities | npm | 11.4.2 | 5 |
| Java | java (openjdk) | 21.0.7 | 5 |
| Go | go | go1.24.3 | 5 |
| Version Control | git | 2.49.0 | 5 |
| JSON Processing | jq | jq-1.7 | 5 |
| Containers | docker | 28.2.2 (Docker Compose v2.36.2) | 5 |

The explicit listing of these preinstalled versions provides a strong signal regarding Jules’ preference for a stable and predictable operating environment. This dictates that the AI must implement a Dependency Mapping Module (DMM) capable of cross-referencing project requirements (e.g., from package.json or requirements.txt) against this Preinstalled Toolchain Catalog. The goal of the DMM is to ensure that generated setup scripts only include commands for installing tool versions or packages that deviate from, or are missing entirely from, the established VM environment, thereby optimizing setup time and stability.

### **II.3. Setup Script Requirements and Snapshot Mechanics**

Setup scripts are fundamentally intended to install project dependencies, configure the environment, and potentially execute initial verification steps like running linters or tests.5 A validation button is provided in the UI to allow for early error detection in the script syntax or execution.5

A critical operational constraint is that setup scripts must be both **lightweight and fast**.5 The inclusion of long-running, non-terminating processes, such as npm run dev (a common daemon startup command), is explicitly documented as a frequent cause of task failure.3 This suggests the presence of an internal timeout or validation rule that flags or fails tasks where the setup phase does not reach termination within an acceptable period.

Consequently, the AI application must incorporate a Setup Script Linter (SSL) that enforces strict adherence to this performance constraint. The SSL must automatically flag and prohibit any known anti-patterns, such as daemon starts or commands that require interactive user input, ensuring the environment setup is strictly limited to idempotent configuration and dependency resolution.

Upon successful execution of a setup script (often triggered by "Run and Snapshot"), Jules captures a snapshot of the configured environment.5 This snapshot is critical for performance in complex environments, as it is reused for all subsequent Jules tasks initiated from that specific repository, bypassing the need for repetitive, time-consuming dependency installations.5 This separation of labor—Configuration (Phase 1: idempotent and snapshot-worthy) and Task Execution (Phase 2: prompt-driven modification)—must be rigidly maintained by the AI agent. Failure in Phase 1 (Setup) should trigger environment debugging, not a task rerun.

## **III. Jules Tools CLI: Command Reference and Contract Specification**

The current documentation focuses heavily on the utilization of the CLI for task initiation and integration with external tools. Detailed references for task status monitoring or result retrieval via the CLI are not documented, suggesting the command-line interface is primarily designed as a task queuing mechanism.

### **III.1. Machine-Readable Command Definition**

The primary command observed in documented automation workflows is jules remote new, used for starting a new work session based on a defined task description.

Table: Jules Tools CLI Command Specification

| Command | Function Description | Syntax | Required Parameters | Notes | Source |
| :---- | :---- | :---- | :---- | :---- | :---- |
| jules remote new | Creates a new, remote Jules session and initiates a task within the specified repository using the supplied task description. | jules remote new \--repo \<repo\_path\> \--session "\<description\>" | \--repo (string, repository path); \--session (string, task description) | The task description is often derived from piped input. | 6 |

### **III.2. Task Initiation Contract**

The jules remote new command establishes the crucial CLI Input Contract for the AI application. While the command accepts a \--repo parameter, often utilized as the current directory (--repo.) in the documented examples, the key instruction vector is the task description passed either via the \--session flag or, more commonly in automated scripting, via standard input piping.6

The documentation’s emphasis on workflows where input is streamed directly into the jules command confirms that the CLI is engineered to consume the final output of a preceding processing chain as its primary instructional payload. For example, the output of a JSON parser (jq) or an external AI prioritization tool (gemini) is piped directly to the \--session parameter of jules remote new.6

This command definition establishes the limit of documented CLI functionality. The absence of documented commands for reading task status, fetching results, or managing running tasks (Implied Task Monitoring Gap) means the AI application must assume the CLI is strictly a task initiator. Any subsequent requirements for monitoring progress or retrieving final patch files will likely necessitate integration with a separate, undocumented API or reliance on polling mechanisms within the web interface.

## **IV. Operational Integration: Workflow Analysis and Composition Patterns**

The value of the Jules Tools CLI within an automated development pipeline is realized through its composition with standard UNIX utilities and external developer tools. The core paradigm involves leveraging shell scripting for data retrieval, formatting, and piping the resultant, focused instruction string into the jules remote new command.6

### **IV.1. Workflow Analysis: Local Task Generation**

This pattern illustrates the conversion of locally maintained data structures into executable Jules sessions. In the documented example, a TODO.md file is parsed line-by-line.6

* **Process:** The script utilizes standard shell constructs (cat, while IFS= read \-r line; do... done) to iterate through the lines of the input file.  
* **Data Flow:** The content of the local file (TODO.md) is read, and each line is assigned as the session description for a new task.6  
* **Directive for AI:** The AI application can utilize this foundational pattern for batch processing internally defined work items, ensuring that the input string passed to the \--session flag corresponds to a single, clear, and specific task definition.

### **IV.2. Workflow Analysis: Integration with Remote APIs (GitHub Issues)**

This workflow demonstrates how the CLI seamlessly integrates with external data sources requiring API interaction and robust data parsing.

* **Process:** The script uses the GitHub CLI (gh) to query assigned issues (gh issue list \--assignee @me \--limit 1\) and requests the output be formatted as JSON, specifically including the title field (--json title).6  
* **Data Parsing:** The intermediate JSON output is immediately processed by the preinstalled JSON processor, jq (version 1.7), which uses the raw output filter (-r) to extract the string value of the issue title (jq \-r '..title').5  
* **Data Flow:** GitHub API $\\rightarrow$ gh CLI $\\rightarrow$ jq (extraction) $\\rightarrow$ Standard Input $\\rightarrow$ jules remote new \--repo..6  
* **Directive for AI:** This pattern establishes the mandatory requirement for robust JSON processing capabilities to interface correctly between external tools and the Jules CLI. The AI must be designed with modularity, capable of generating precise query parameters for tools like gh and utilizing jq for deterministic field extraction.

### **IV.3. Workflow Analysis: AI-Driven Task Prioritization**

This is the most critical integration pattern, showcasing the Jules CLI as the execution layer downstream of a complex, external AI analysis process.

* **Process:** The script retrieves a list of assigned GitHub issues using gh issue list and pipes this raw data, along with a directive prompt ("find the most tedious issue, print it verbatim\\n"), into the external gemini CLI tool.6  
* **Intermediate Analysis:** The Gemini CLI analyzes the issue backlog and, based on the strict prompt, outputs the title of the selected issue verbatim.  
* **Data Flow:** GitHub Issues $\\rightarrow$ gemini CLI (selection) $\\rightarrow$ Verbatim Output $\\rightarrow$ Standard Input $\\rightarrow$ jules remote new \--repo..6  
* **Directive for AI:** Complex AI selection, prioritization, or analysis must occur *before* the Jules session creation. The input string provided to the jules command must be the final, concise, and verbatim output of the preceding processing step. This adheres to the specific prompt requirement (Section I.2). The use of the jq filter (-r) and the requirement for "verbatim" output confirms that the session description input requires a clean, simple string, devoid of JSON formatting, control characters, or unnecessary multi-line documentation. The AI pre-processing workflow must include a final sanitization layer to enforce this clean Input Formatting Constraint.

## **V. Resilience and Failure Mode Analysis for AI Agents**

For reliable and high-throughput automation, the AI application must be architected with proactive mechanisms to manage operational constraints and anticipate documented failure modes.

### **V.1. Usage Constraints and Limits Management**

Jules enforces strict usage limits based on the user's subscription plan. These limits are defined across three tiers, and the AI agent must incorporate an internal mechanism to track and enforce these constraints to prevent task submission that will inevitably fail due to capacity exhaustion.3

Table: Jules Plan Operational Limits

| Plan Tier | Daily Tasks (Rolling 24h) | Concurrent Tasks | Model Access |
| :---- | :---- | :---- | :---- |
| Jules | 15 | 3 | Gemini 2.5 Pro |
| Jules in Pro | 100 | 15 | Higher access to the latest model (starting with Gemini 2.5 Pro) |
| Jules in Ultra | 300 | 60 | Priority access to the latest model (starting with Gemini 2.5 Pro) |

These limits operate on a rolling 24-hour window.3 When a user reaches their daily task limit, the functionality to trigger new tasks is explicitly disabled, and an error notification is surfaced.3 However, the user retains access to review or manage tasks that are already active, and task history remains unaffected.3

The consequence for the AI application is the mandatory implementation of a Rate Limiting Module (RLM) tied directly to the subscribed plan tier. Because the limit operates on a rolling window, the RLM should utilize a Predictive Scheduling Engine (PSE) capable of tracking usage over time and forecasting the reset window. This proactive approach ensures that task submission maximizes throughput while remaining compliant, avoiding the inefficiency of hitting a hard failure at the limit.

### **V.2. Catalog of Failure Vectors and Mitigation Strategies**

Failures in Jules tasks are often attributable to controllable aspects of environment preparation and instruction quality. The AI must prioritize mitigation at the preparation stage by validating its inputs against these known failure vectors.

The most frequent issues that cause task failures are categorized as follows 3:

1. **Incomplete or missing environment setup scripts:** This is a fundamental configuration deficiency, solvable by enforcing the DMM (Dependency Mapping Module) to ensure all project requirements are covered in the setup script.  
2. **Prompts that are too vague or overly broad:** This is an instructional deficiency, solved by enforcing the PSV (Prompt Specificity Validator) to ensure targeted, unambiguous instructions.  
3. **Repos with unusual or nonstandard build systems:** This requires a highly explicit and verbose setup script to correctly define build procedures.  
4. **Long-running processes (like npm run dev) included in setup:** This is an execution constraint violation, solvable by enforcing the SSL (Setup Script Linter) to prohibit non-terminating commands and long build times.

### **V.3. Error Handling and Resilience Policy**

Jules features internal mechanisms for handling transient errors. The system will automatically attempt retries for failures categorized as temporary, such as network hiccups, transient installation errors, or slow dependency resolutions.3 The AI should account for this automatic resilience, allowing a reasonable latency period before assuming a hard failure.

In the case of persistent failures, the required solution documented for manual intervention involves modifying the system inputs: specifically, clicking rerun, modifying the setup script, or refining the prompt before attempting a restart, while addressing specific feedback from the failure logs.3 This reinforces that configuration and instruction inputs are the most common sources of persistent failure. Therefore, the AI’s failure management subsystem must focus its automated debugging efforts on refining these inputs (Resilience through Configuration Modification) before escalating the task for human intervention.

### **V.4. Critical Data Gaps and Error Classification**

A major limitation for designing highly deterministic automation is the explicit absence of documented specific exit codes for the Jules CLI.3 In standard automation practices, numerical exit codes are critical for classifying failures (e.g., distinguishing an authentication failure from a timeout).

Due to this data gap, the AI application cannot rely on the standard shell return status of the jules command to definitively classify the nature of a failure. The AI must instead rely on parsing textual error messages and logs surfaced in the activity feed or through available API endpoints.4 This necessitates the integration of a Fuzzy Log Analysis (FLA) component. The FLA component is mandated to use pattern matching against known textual failure outputs (such as keywords like "limit reached," "timeout," or "dependency not found") to classify the failure severity and suggest an appropriate automated mitigation strategy (Mandatory Fuzzy Error Parsing).

## **Conclusions and Architectural Recommendations**

The successful integration of the Jules Tools CLI into an AI-driven automation pipeline depends less on the CLI's command breadth and more on the proactive management of environmental constraints, usage limits, and input quality. The CLI’s primary documented function is a task queue initiator (jules remote new), relying on standard UNIX stream processing to accept task descriptions from highly structured pre-processing steps.

The analysis dictates a mandated architecture for the AI application, composed of five core modules designed to mitigate the primary documented failure vectors and manage operational constraints:

1. **Prompt Specificity Validator (PSV):** Enforces a clear, specific structure for the task instruction string, directly addressing the risk of failure from vague or broad prompts.2  
2. **Dependency Mapping Module (DMM):** Optimizes setup scripts by cross-referencing project requirements against the fixed Preinstalled Toolchain Catalog of the Ubuntu Linux VM.5  
3. **Setup Script Linter (SSL):** Prohibits known anti-patterns, specifically long-running or non-terminating commands, which are documented causes of task failure.4  
4. **Rate Limiting Module (RLM):** Implements usage tracking over a rolling 24-hour window, using a Predictive Scheduling Engine to ensure task submission remains within the defined plan limits (15, 100, or 300 daily tasks).3  
5. **Fuzzy Log Analysis (FLA):** Compensates for the critical lack of specific exit codes by analyzing textual error logs and the activity feed to classify failures and initiate appropriate automated debugging steps, such as refining the setup script or prompt.3

By adhering to these architectural mandates, the AI application can transform the Jules CLI from a simple command-line utility into a reliable, deterministic execution layer within an advanced developer toolchain.

#### **Works cited**

1. Jules Tools Reference | Jules, accessed November 4, 2025, [https://jules.google/docs/cli/reference](https://jules.google/docs/cli/reference)  
2. Getting started \- Jules, accessed November 4, 2025, [https://jules.google/docs/](https://jules.google/docs/)  
3. Limits and Plans | Jules, accessed November 4, 2025, [https://jules.google/docs/usage-limits/](https://jules.google/docs/usage-limits/)  
4. Errors and failures | Jules, accessed November 4, 2025, [https://jules.google/docs/errors/](https://jules.google/docs/errors/)  
5. Environment setup | Jules, accessed November 4, 2025, [https://jules.google/docs/environment/](https://jules.google/docs/environment/)  
6. Practical Examples & Scripting | Jules, accessed November 4, 2025, [https://jules.google/docs/cli/examples](https://jules.google/docs/cli/examples)