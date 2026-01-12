// CONFIGURACIÓN
const API_URL = 'http://127.0.0.1:5000/api'
let currentUserId = localStorage.getItem('cau_user_id')
let currentUserName = localStorage.getItem('cau_user_name')

// INICIALIZACIÓN
window.onload = () => {
  if (currentUserId) {
    mostrarApp(currentUserName)
  }
}

// --- FUNCIONES DE LOGIN ---
async function hacerLogin() {
  const idInput = document.getElementById('userIdInput').value
  const errorMsg = document.getElementById('loginError')

  if (!idInput) return

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: idInput })
    })

    const data = await response.json()

    // CHIVATO: Mira esto en la consola del navegador (F12)
    console.log('📡 Datos recibidos del servidor:', data)

    // Verificamos si la respuesta fue exitosa (código 200)
    if (response.ok) {
      // TRUCO: Buscamos el ID y Nombre en los dos formatos posibles
      // Tu Python manda 'user_id' suelto, mi código anterior buscaba 'data.user.id'
      currentUserId = data.user_id || (data.user && data.user.id)
      currentUserName =
        data.nombre ||
        data.user_name ||
        (data.user && data.user.name) ||
        'Usuario'

      if (currentUserId) {
        // ¡ÉXITO! Guardamos y entramos
        localStorage.setItem('cau_user_id', currentUserId)
        localStorage.setItem('cau_user_name', currentUserName)
        mostrarApp(currentUserName)
      } else {
        throw new Error(
          'El servidor respondió OK, pero no encuentro el ID en los datos.'
        )
      }
    } else {
      // Si el servidor dice que no (401, 404...)
      // Tu Python usa 'mensaje', otros usan 'error'. Leemos ambos.
      errorMsg.innerText = data.error || data.mensaje || 'Usuario no encontrado'
      errorMsg.style.display = 'block'
    }
  } catch (error) {
    console.error('❌ Error JS:', error)
    // Aquí es donde te salía el error antes
    errorMsg.innerText = 'Error: ' + error.message
    errorMsg.style.display = 'block'
  }
}

function logout() {
  localStorage.clear()
  location.reload()
}

function mostrarApp(nombre) {
  document.getElementById('login-screen').style.display = 'none'
  document.getElementById('app-container').style.display = 'flex'
  document.getElementById('userNameDisplay').innerText = nombre
}

// --- FUNCIONES DE CHAT ---
async function enviarMensaje() {
  const input = document.getElementById('userMessage')
  const texto = input.value.trim()
  if (!texto) return

  // 1. Mostrar mensaje usuario
  agregarBurbuja(texto, 'user')
  input.value = ''

  // 2. Mostrar "Escribiendo..."
  const loadingId = agregarBurbuja('Analizando...', 'bot', true)

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUserId,
        mensaje: texto
      })
    })

    const data = await response.json()

    // 3. Quitar loading y mostrar respuesta
    eliminarBurbuja(loadingId)

    if (data.error) {
      agregarBurbuja('Error: ' + data.error, 'bot')
    } else {
      agregarBurbuja(data.respuesta, 'bot')
      agregarEtiquetas(data) // Mostrar badges
    }
  } catch (error) {
    eliminarBurbuja(loadingId)
    agregarBurbuja('Error de conexión.', 'bot')
  }
}

function agregarBurbuja(texto, tipo, esLoading = false) {
  const chatDiv = document.getElementById('chat-history')
  const msgDiv = document.createElement('div')
  msgDiv.className = `message ${tipo}-msg`
  msgDiv.innerText = texto
  if (esLoading) msgDiv.id = 'loading-bubble'

  chatDiv.appendChild(msgDiv)
  chatDiv.scrollTop = chatDiv.scrollHeight
  return msgDiv.id
}

function eliminarBurbuja(id) {
  const el = document.getElementById(id)
  if (el) el.remove()
}

function agregarEtiquetas(data) {
  const chatDiv = document.getElementById('chat-history')
  const badgeDiv = document.createElement('div')
  badgeDiv.className = 'badges'
  badgeDiv.innerHTML = `
        <span class="badge bg-cat">${data.categoria || 'N/A'}</span>
        <span class="badge bg-urg">${data.urgencia || 'N/A'}</span>
    `
  // Añadir debajo del último mensaje
  chatDiv.appendChild(badgeDiv)
  chatDiv.scrollTop = chatDiv.scrollHeight
}

// --- FUNCIONES DE NAVEGACIÓN ---
function mostrarVista(vista) {
  document.getElementById('chat-view').style.display =
    vista === 'chat' ? 'flex' : 'none'
  document.getElementById('history-view').style.display =
    vista === 'historial' ? 'block' : 'none'
}

// --- HISTORIAL ---
async function cargarHistorial() {
  mostrarVista('historial')
  const filtro = document.getElementById('catFilter').value

  let url = `${API_URL}/consultas?user_id=${currentUserId}`
  if (filtro) url += `&categoria=${filtro}`

  const res = await fetch(url)
  const datos = await res.json()

  const tbody = document.querySelector('#historyTable tbody')
  tbody.innerHTML = ''

  datos.forEach((item) => {
    const row = `<tr>
            <td>${item.fecha}</td>
            <td>${item.pregunta}</td>
            <td>${item.respuesta.substring(0, 50)}...</td>
            <td>${item.categoria}</td>
        </tr>`
    tbody.innerHTML += row
  })
}
