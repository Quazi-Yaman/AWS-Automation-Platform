const serviceSelect = document.getElementById("serviceSelect");
const operationSelect = document.getElementById("operationSelect");

const s3Form = document.getElementById("s3Form");
const dynamodbForm = document.getElementById("dynamodbForm");
const lambdaForm = document.getElementById("lambdaForm");

const automationResult = document.getElementById("automationResult");
const createResourceButton = document.getElementById("createResourceButton");

const API_BASE_URL = "http://127.0.0.1:5000/api";


/* =========================================
   SERVICE / ACTION OPTIONS
========================================= */

const serviceOperations = {
    s3: [
    {
        value: "create_bucket",
        label: "Create Bucket"
    },
    {
        value: "list_buckets",
        label: "List Buckets"
    },
    {
        value: "head_bucket",
        label: "Check Bucket"
    },
    {
        value: "delete_bucket",
        label: "Delete Bucket"
    }
],

    dynamodb: [
        {
            value: "create_table",
            label: "Create Table"
        },
        {
            value: "list_tables",
            label: "List Tables"
        },
        {
            value: "describe_table",
            label: "Describe Table"
        },
        {
            value: "delete_table",
            label: "Delete Table"
        }
    ],

    lambda: [
        {
            value: "create_function",
            label: "Create Function"
        },
        {
            value: "list_functions",
            label: "List Functions"
        },
        {
            value: "get_function",
            label: "Get Function"
        }
    ]
};


/* =========================================
   BACKEND CONNECTION
========================================= */

async function checkBackend() {
    const statusElement =
        document.getElementById("connectionStatus");

    try {
        const response = await fetch(
            `${API_BASE_URL}/health`
        );

        const data = await response.json();

        if (response.ok && data.success !== false) {
            statusElement.textContent = "🟢 Backend Connected";
            statusElement.style.color = "#047857";
        } else {
            statusElement.textContent = "🔴 Backend Error";
            statusElement.style.color = "#b91c1c";
        }

    } catch (error) {
        statusElement.textContent = "🔴 Backend Offline";
        statusElement.style.color = "#b91c1c";
    }
}


/* =========================================
   SERVICE SELECT
========================================= */

function updateOperations() {
    const service = serviceSelect.value;

    operationSelect.innerHTML = "";

    const operations =
        serviceOperations[service] || [];

    operations.forEach(operation => {
        const option = document.createElement("option");

        option.value = operation.value;
        option.textContent = operation.label;

        operationSelect.appendChild(option);
    });

    updateForms();
}


/* =========================================
   FORM DISPLAY
========================================= */

function updateForms() {
    const service = serviceSelect.value;
    const operation = operationSelect.value;

    s3Form.classList.add("hidden");
    dynamodbForm.classList.add("hidden");
    lambdaForm.classList.add("hidden");

    if (service === "s3") {
        s3Form.classList.remove("hidden");
    }

    if (service === "dynamodb") {
        dynamodbForm.classList.remove("hidden");
    }

    if (service === "lambda") {
        lambdaForm.classList.remove("hidden");
    }

    if (operation === "list_buckets") {
        s3Form.classList.add("hidden");
    }

    if (operation === "list_tables") {
        dynamodbForm.classList.add("hidden");
    }

    if (operation === "list_functions") {
        lambdaForm.classList.add("hidden");
    }
}


/* =========================================
   BUILD PARAMETERS
========================================= */

function buildParameters() {
    const service = serviceSelect.value;
    const operation = operationSelect.value;

    if (service === "s3") {

        if (operation === "create_bucket") {

            const bucketName =
                document.getElementById("bucketName").value.trim();

            const region =
                document.getElementById("bucketRegion").value;

            return {
                Bucket: bucketName,
                Region: region
            };
        }

        if (operation === "head_bucket") {

            const bucketName =
                document.getElementById("bucketName").value.trim();

            return {
                Bucket: bucketName
            };
        }

        return {};
    }


    if (service === "dynamodb") {

        if (
            operation === "create_table"
        ) {

            const tableName =
                document.getElementById("tableName").value.trim();

            const partitionKey =
                document.getElementById("partitionKey").value.trim();

            const keyType =
                document.getElementById("keyType").value;

            return {
                TableName: tableName,

                KeySchema: [
                    {
                        AttributeName: partitionKey,
                        KeyType: "HASH"
                    }
                ],

                AttributeDefinitions: [
                    {
                        AttributeName: partitionKey,
                        AttributeType: keyType
                    }
                ],

                BillingMode: "PAY_PER_REQUEST"
            };
        }


        if (
            operation === "describe_table" ||
            operation === "delete_table"
        ) {

            const tableName =
                document.getElementById("tableName").value.trim();

            return {
                TableName: tableName
            };
        }

        return {};
    }


    if (service === "lambda") {

        if (operation === "create_function") {

            const functionName =
                document.getElementById("functionName").value.trim();

            const runtime =
                document.getElementById("lambdaRuntime").value;

            const handler =
                document.getElementById("lambdaHandler").value.trim();

            const role =
                document.getElementById("lambdaRole").value.trim();

            const code =
                document.getElementById("lambdaCode").value;

            return {
                FunctionName: functionName,
                Runtime: runtime,
                Handler: handler,
                Role: role,
                CodeText: code
            };
        }


        if (
            operation === "get_function"
        ) {

            const functionName =
                document.getElementById("functionName").value.trim();

            return {
                FunctionName: functionName
            };
        }

        return {};
    }

    return {};
}


/* =========================================
   AUTOMATION
========================================= */

async function createResource() {

    const service = serviceSelect.value;
    const operation = operationSelect.value;

    const parameters =
        buildParameters();


    /* Basic validation */

    if (
        operation === "create_bucket" &&
        !parameters.Bucket
    ) {
        showAutomationResult(
            "error",
            "❌ Bucket name is required."
        );
        return;
    }


    if (
        operation === "create_table" &&
        (
            !parameters.TableName ||
            !parameters.KeySchema?.[0]?.AttributeName
        )
    ) {
        showAutomationResult(
            "error",
            "❌ Table name and partition key are required."
        );
        return;
    }


    if (
        operation === "create_function" &&
        (
            !parameters.FunctionName ||
            !parameters.Handler ||
            !parameters.Role ||
            !parameters.CodeText
        )
    ) {
        showAutomationResult(
            "error",
            "❌ Function name, handler, IAM role and Lambda code are required."
        );
        return;
    }


    createResourceButton.disabled = true;

    showAutomationResult(
        "info",
        `⏳ Running ${service.toUpperCase()} ${operation}...`
    );


    try {

        const response = await fetch(
            `${API_BASE_URL}/automation`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    service: service,
                    operation: operation,
                    parameters: parameters
                })
            }
        );


        const data =
            await response.json();


        if (data.success) {

            let message =
                `✅ ${service.toUpperCase()} ${operation} completed successfully.`;

            if (data.method) {
                message +=
                    ` Method: ${data.method}.`;
            }

            if (data.fallback_used) {
                message +=
                    " AWS CLI fallback was used.";
            }

            showAutomationResult(
                "success",
                message
            );

        } else {

            let errorMessage =
                data.error ||
                "AWS operation failed.";

            if (data.boto3?.error) {
                errorMessage +=
                    ` Boto3: ${data.boto3.error}`;
            }

            if (data.cli?.error) {
                errorMessage +=
                    ` CLI: ${data.cli.error}`;
            }

            showAutomationResult(
                "error",
                `❌ ${errorMessage}`
            );
        }


        await loadActivity();
        await loadServiceStatus();


    } catch (error) {

        showAutomationResult(
            "error",
            `❌ Request failed: ${error.message}`
        );

    } finally {

        createResourceButton.disabled = false;
    }
}


/* =========================================
   RESULT MESSAGE
========================================= */

function showAutomationResult(
    type,
    message
) {

    automationResult.className =
        `automation-result ${type}`;

    automationResult.textContent =
        message;
}


/* =========================================
   SERVICE STATUS
========================================= */

async function loadServiceStatus() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/status`
        );

        const data =
            await response.json();


        if (!data.resources) {
            return;
        }


        Object.entries(
            data.resources
        ).forEach(
            ([service, information]) => {

                const element =
                    document.getElementById(
                        `${service}Status`
                    );

                if (!element) {
                    return;
                }

                if (
                    information.status ===
                    "available"
                ) {

                    element.textContent =
                        `🟢 Available (${information.method})`;

                    element.style.color =
                        "#047857";

                } else {

                    element.textContent =
                        "🔴 Unavailable";

                    element.style.color =
                        "#b91c1c";
                }
            }
        );

    } catch (error) {

        console.error(
            "Service status error:",
            error
        );
    }
}


/* =========================================
   ACTIVITY LOG
========================================= */

async function loadActivity() {

    const activityLog =
        document.getElementById(
            "activityLog"
        );

    try {

        const response = await fetch(
            `${API_BASE_URL}/activity`
        );

        const data =
            await response.json();


        if (
            !data.success ||
            !data.result
        ) {

            activityLog.innerHTML =
                "<p>No activity found.</p>";

            return;
        }


        const items =
            data.result.Items || [];


        if (items.length === 0) {

            activityLog.innerHTML =
                "<p>No activity yet.</p>";

            return;
        }


        items.sort(
            (a, b) => {

                const timeA =
                    a.timestamp?.S || "";

                const timeB =
                    b.timestamp?.S || "";

                return timeB.localeCompare(
                    timeA
                );
            }
        );


        activityLog.innerHTML = "";


        items.forEach(item => {

            const status =
                item.status?.S || "info";

            const action =
                item.action?.S || "AWS Action";

            const message =
                item.message?.S || "";

            const resource =
                item.resource?.S || "";

            const method =
                item.method?.S || "";

            const timestamp =
                item.timestamp?.S || "";


            const activityItem =
                document.createElement(
                    "div"
                );

            activityItem.className =
                "activity-item";


            const icon =
                status === "success"
                    ? "✅"
                    : status === "error"
                        ? "❌"
                        : "ℹ️";


            activityItem.innerHTML = `
                <div class="activity-icon">
                    ${icon}
                </div>

                <div class="activity-content">

                    <div class="activity-title">
                        ${action}
                    </div>

                    <div class="activity-details">
                        ${message}
                    </div>

                    ${
                        resource
                            ? `<div class="activity-details">
                                Resource: ${resource}
                               </div>`
                            : ""
                    }

                    ${
                        method
                            ? `<div class="activity-details">
                                Method: ${method}
                               </div>`
                            : ""
                    }

                    <div class="activity-time">
                        ${timestamp}
                    </div>

                </div>
            `;


            activityLog.appendChild(
                activityItem
            );
        });


    } catch (error) {

        activityLog.innerHTML =
            `<p>Unable to load activity: ${error.message}</p>`;
    }
}


/* =========================================
   EVENT LISTENERS
========================================= */

serviceSelect.addEventListener(
    "change",
    updateOperations
);

operationSelect.addEventListener(
    "change",
    updateForms
);

createResourceButton.addEventListener(
    "click",
    createResource
);


/* =========================================
   INITIAL LOAD
========================================= */

updateOperations();

checkBackend();

loadActivity();

loadServiceStatus();


/* Refresh every 5 seconds */

setInterval(
    loadActivity,
    5000
);

setInterval(
    loadServiceStatus,
    5000
);