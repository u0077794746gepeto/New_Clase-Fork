// 1. Efectos visuales para los campos del formulario
const inputs = document.querySelectorAll("input");

inputs.forEach(input => {
    input.addEventListener("focus", () => {
        input.style.transform = "scale(1.05)";
    });

    input.addEventListener("blur", () => {
        input.style.transform = "scale(1)";
    });
});



// 2. Configuración de la API (Seguridad mejorada)
// Usamos la variable que definimos en el HTML (base.html)
const API_KEY = API_KEY_FROM_SERVER; 
const CIUDAD = 'Santander'; 
const URL = `https://api.openweathermap.org/data/2.5/weather?q=${CIUDAD}&units=metric&lang=es&appid=${API_KEY}`;

// 3. Función para mostrar el clima en la academia
function cargarClima() {
    if (!API_KEY) return console.warn("Falta la clave de la API");

    fetch(URL)
        .then(respuesta => {
            if (!respuesta.ok) throw new Error("Error en la petición");
            return respuesta.json();
        })
        .then(datos => {
            const temp = Math.round(datos.main.temp);
            const desc = datos.weather[0].description;
            const icono = datos.weather[0].icon;
            const urlIcono = `https://openweathermap.org/img/wn/${icono}@2x.png`;

            const cajaClima = document.getElementById('clima');
            cajaClima.innerHTML = `
                <img src="${urlIcono}" alt="Icono del tiempo" style="width:50px; vertical-align:middle;">
                <span>${CIUDAD}: ${temp}°C, ${desc}</span>
            `;
            
            cajaClima.style.opacity = "1";
        })
        .catch(error => {
            console.error('Hubo un problema:', error);
            document.getElementById('clima').innerHTML = "Clima no disponible ahora";
        });
}

// Arrancamos la función al entrar en la web
window.onload = cargarClima;

//hago un cambio