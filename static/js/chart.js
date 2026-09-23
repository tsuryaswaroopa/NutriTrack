// Pie Chart

const chartCanvas = document.getElementById("nutritionChart");

if (chartCanvas) {

    new Chart(chartCanvas, {

        type: "pie",

        data: {

            labels: [

                "Protein",
                "Carbs",
                "Fat"

            ],

            datasets: [{

                data: nutritionData,

                backgroundColor: [

                    "#0d6efd",
                    "#ffc107",
                    "#198754"

                ],

                borderWidth: 2

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                }

            }

        }

    });

}

// Search Function

const searchInput = document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        let value = this.value.toLowerCase();

        let rows = document.querySelectorAll("#foodTable tbody tr");

        rows.forEach(function (row) {

            if (row.innerText.toLowerCase().includes(value)) {

                row.style.display = "";

            } else {

                row.style.display = "none";

            }

        });

    });

}