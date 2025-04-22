document.addEventListener("DOMContentLoaded", function() {
    const calendarContainer = document.getElementById("calendar-container");
    const dateInput = document.getElementById("reservation-date");
    const timeButton = document.getElementById("search-time");
     fechaReserva = "";
  
      // Calcula las fechas mínima y máxima
      const today = new Date();
      const maxDate = new Date();
      maxDate.setDate(today.getDate() + 30); // 30 días a partir de hoy
  
      // Formatea las fechas en "YYYY-MM-DD"
      const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
  
      // Asigna las fechas mínima y máxima al input
      dateInput.min = formatDate(today);    // Fecha mínima: Hoy
      dateInput.max = formatDate(maxDate); // Fecha máxima: Dentro de 30 días
      
      timeButton.addEventListener("click",function() {
        fechaReserva = dateInput.value;//se guarda la fecha seleccionada por el usuario
        if(fechaReserva != "")
          {
            fetch('/guardarDatos/', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken') // Token CSRF para seguridad en Django
              },
              body: JSON.stringify({ fecha: fechaReserva })
          })
          .then(response => response.json())
          .then(() => {
            window.location.href = "/hora/"; //abrir hora.html;
          })
          .catch(error => console.error("Error al guardar la fecha:", error));
          }
        
        else
          {alert("por favor selecciona una fecha para continuar");}
      });
    });

    function getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue};