function fetchEmployeeName() {
  var employeeRut = document.getElementById("employee_rut").value; // Cambiado de employee_id a employee_rut
  var employeeNameSpan = document.getElementById("employee_name");

  if (employeeRut) {
    fetch(`/get_employee_name/${employeeRut}`) // Modificado para usar el RUT
      .then((response) => {
        if (response.ok) {
          return response.text();
        } else {
          return "Does not exist";
        }
      })
      .then((data) => {
        employeeNameSpan.innerText = "Employee name: " + data;
      })
      .catch((error) => {
        employeeNameSpan.innerText = "Error fetching employee name.";
      });
  } else {
    employeeNameSpan.innerText = "Enter RUT to fetch name"; // Modificado el texto indicativo
  }
}

// Function to update the rating based on evaluation factor (grade)
function updateRating() {
  const evaluationFactor = parseFloat(
    document.getElementById("evaluation_factor").value
  );
  let rating = "";

  if (evaluationFactor === 7) {
    rating = "Excellent";
  } else if (evaluationFactor >= 6.5 && evaluationFactor < 7) {
    rating = "Very Good";
  } else if (evaluationFactor >= 6 && evaluationFactor < 6.5) {
    rating = "Good";
  } else if (evaluationFactor >= 5 && evaluationFactor < 6) {
    rating = "Satisfactory";
  } else if (evaluationFactor >= 4 && evaluationFactor < 5) {
    rating = "Fair";
  } else if (evaluationFactor < 4) {
    rating = "Deficient";
  }

  // Set the calculated rating in the input field
  document.getElementById("rating").value = rating;
}

//Updates the "Days Taken" field based on the start and end dates.
function updateDaysTaken() {
  const startDate = new Date(document.getElementById("start_date").value);
  const endDate = new Date(document.getElementById("end_date").value);

  if (!isNaN(startDate) && !isNaN(endDate) && endDate >= startDate) {
    const differenceInTime = endDate - startDate;
    const daysTaken = Math.ceil(differenceInTime / (1000 * 60 * 60 * 24)) + 1; // Include both start and end dates
    document.getElementById("days_taken").value = daysTaken;
  } else {
    document.getElementById("days_taken").value = "";
  }
}

//Updates the "Accumulated Days" field based on the checkbox status.
 
function updateAccumulatedDays() {
  const checkbox = document.getElementById("long_service_employee");
  const accumulatedDaysField = document.getElementById("accumulated_days");
  accumulatedDaysField.value = checkbox.checked ? 20 : 15;
}
