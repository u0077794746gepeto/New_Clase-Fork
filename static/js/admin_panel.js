/**
 * admin_panel.js
 * Gestión del panel de administración
 */

document.getElementById('btn-usuarios').addEventListener('click', function() {
    const url = this.dataset.url;
    if (url) window.location.href = url;
});

document.getElementById('btn-asignaturas').addEventListener('click', function() {
    console.log('Abriendo gestor de asignaturas');
});

document.getElementById('btn-horarios').addEventListener('click', function() {
    console.log('Abriendo gestor de horarios');
});

document.getElementById('btn-reportes').addEventListener('click', function() {
    console.log('Abriendo reportes');
});

document.getElementById('btn-configuracion').addEventListener('click', function() {
    console.log('Abriendo configuración');
});

document.getElementById('btn-nuevo').addEventListener('click', function() {
    console.log('Abriendo nuevo módulo');
});

document.getElementById('btn-cerrar').addEventListener('click', function() {
    const url = this.dataset.url;
    if (url) window.location.href = url;
});