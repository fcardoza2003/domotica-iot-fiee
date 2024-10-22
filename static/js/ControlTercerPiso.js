// Función para actualizar el estado de las luces (LEDs) del tercer piso
function actualizarEstado() {
    fetch('http://4.227.157.228:8000/api/getledstatus?esp_id=ESP32_03')  // Incluye el esp_id en la URL
        .then(response => response.json())
        .then(data => {
            console.log("Estado de los LEDs:", data); // Verificar estado de los LEDs en la consola

            // Actualizar estados individuales
            for (let i = 3; i <= 9; i++) {  // Cambiado de 3 a 9 para controlar led3_status hasta led9_status
                const ledStatus = data[`led${i}_status`];
                const ledSwitch = document.getElementById(`led${i}-switch`);
                const ledLabel = document.getElementById(`led${i}-status`);

                if (ledSwitch && ledLabel) {  // Verificar que los elementos existen
                    ledSwitch.checked = ledStatus == 1;
                    ledLabel.innerText = ledStatus == 1 ? `Luz ${i} encendida` : `Luz ${i} apagada`;
                }
            }

            // Verificar si todas las luces están encendidas para actualizar el switch general
            const allOn = [data.led3_status, data.led4_status, data.led5_status, data.led6_status, data.led7_status, data.led8_status, data.led9_status].every(status => status == 1);
            document.getElementById('general-switch').checked = allOn;
        })
        .catch(error => {
            console.error("Error al obtener el estado de los LEDs:", error);
            for (let i = 3; i <= 9; i++) {  // Mismo rango que antes (3 a 9)
                const ledLabel = document.getElementById(`led${i}-status`);
                if (ledLabel) {
                    ledLabel.innerText = 'Error al cargar';
                }
            }
        });
}

// Función para cambiar el estado de los LEDs cuando se activa el interruptor individual
function toggleLED(ledNumber) {
    const ledState = document.getElementById(`led${ledNumber}-switch`).checked ? 1 : 0;
    fetch('http://4.227.157.228:8000/api/updateled', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `esp_id=ESP32_03&led${ledNumber}_status=${ledState}`
    })
    .then(response => {
        if (response.ok) {
            console.log(`Estado del LED ${ledNumber} actualizado`);
            document.getElementById(`led${ledNumber}-status`).innerText = ledState == 1 ? `Luz ${ledNumber} encendida` : `Luz ${ledNumber} apagada`;
        } else {
            console.error(`Error al actualizar el estado del LED ${ledNumber}`);
        }
    })
    .catch(error => {
        console.error(`Error al cambiar el estado del LED ${ledNumber}:`, error);
        document.getElementById(`led${ledNumber}-status`).innerText = `Error al actualizar la Luz ${ledNumber}`;
    });
}

// Función para encender o apagar todas las luces usando el switch general
function toggleGeneralSwitch() {
    const generalState = document.getElementById('general-switch').checked ? 1 : 0;

    // Encender o apagar todas las luces (LEDs desde 3 hasta 9)
    for (let i = 3; i <= 9; i++) {
        // Actualizamos el estado de cada LED
        fetch('http://4.227.157.228:8000/api/updateled', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `esp_id=ESP32_03&led${i}_status=${generalState}`
        })
        .then(response => {
            if (response.ok) {
                console.log(`Estado del LED ${i} actualizado por el control general`);
                document.getElementById(`led${i}-switch`).checked = generalState == 1;
                document.getElementById(`led${i}-status`).innerText = generalState == 1 ? `Luz ${i} encendida` : `Luz ${i} apagada`;
            } else {
                console.error(`Error al actualizar el estado del LED ${i}`);
            }
        })
        .catch(error => {
            console.error(`Error al cambiar el estado del LED ${i} por el control general:`, error);
        });
    }
}

// Llamar a la función para actualizar el estado al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    actualizarEstado(); // Actualizar estado inmediatamente al cargar la página

    // Establecer intervalo para actualizar el estado cada 5 segundos
    setInterval(actualizarEstado, 5000);

    // Escuchar el evento de cambio en los switches de las luces individuales (LEDs desde 3 hasta 9)
    for (let i = 3; i <= 9; i++) {
        document.getElementById(`led${i}-switch`).addEventListener('change', function() {
            toggleLED(i);
        });
    }

    // Escuchar el evento de cambio en el switch general
    document.getElementById('general-switch').addEventListener('change', toggleGeneralSwitch);
});
