// CONFIGURACIÓN DINÁMICA (Para Local y AWS)
// Esto detecta automáticamente la IP o Dominio desde donde se carga la web
const protocol = window.location.protocol // http: o https:
const hostname = window.location.hostname // 'localhost' o '34.22.xx.xx'
const backendPort = '5000' // El puerto donde escucha tu Flask

// Construimos la URL final automáticamente
const API_URL = `${protocol}//${hostname}:${backendPort}/api`

console.log('Conectando al backend en:', API_URL) // Para depuración

let currentUserId = localStorage.getItem('cau_user_id')
let currentUserName = localStorage.getItem('cau_user_name')

// INICIALIZACIÓN
window.onload = () => {
  if (currentUserId) {
    mostrarApp(currentUserName)
  }
}

// --- LOGIN ---
async function hacerLogin() {
  const idInput = document.getElementById('userIdInput').value
  const errorMsg = document.getElementById('loginError')

  if (!idInput) return

  errorMsg.style.display = 'none'

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: idInput })
    })

    const data = await response.json()

    if (response.ok) {
      currentUserId = data.user_id || (data.user && data.user.id)
      // Fallback a 'Ingeniero' si no viene nombre
      currentUserName =
        data.nombre ||
        data.user_name ||
        (data.user && data.user.name) ||
        'Ingeniero'

      if (currentUserId) {
        localStorage.setItem('cau_user_id', currentUserId)
        localStorage.setItem('cau_user_name', currentUserName)
        mostrarApp(currentUserName)
      } else {
        throw new Error('ID no reconocido.')
      }
    } else {
      mostrarErrorLogin(data.error || 'Credenciales no válidas')
    }
  } catch (error) {
    console.error(error) // Ver error en consola
    mostrarErrorLogin('No se pudo conectar con el servidor.')
  }
}

function mostrarErrorLogin(msg) {
  const el = document.getElementById('loginError')
  el.innerText = msg
  el.style.display = 'block'
}

function logout() {
  localStorage.clear()
  location.reload()
}

// --- UI PRINCIPAL ---
function mostrarApp(nombre) {
  document.getElementById('login-screen').style.display = 'none'
  document.getElementById('app-container').style.display = 'flex'
  document.getElementById('userNameDisplay').innerText = nombre

  // **MEJORA UX:** Saludo Personalizado Dinámico
  const welcomeMsg = document.getElementById('bot-welcome')
  if (welcomeMsg) {
    // Usamos innerHTML por si queremos poner el nombre en negrita
    welcomeMsg.innerHTML = `Hola <strong>${nombre}</strong>, bienvenido al soporte de ingeniería. ¿En qué te puedo ayudar hoy?`
  }
}

// --- CHAT LOGIC ---
async function enviarMensaje() {
  const input = document.getElementById('userMessage')
  const texto = input.value.trim()
  if (!texto) return

  // 1. Mostrar mensaje usuario
  agregarBurbuja(texto, 'user')
  input.value = ''

  // 2. Mostrar "Thinking..." animado (UX Mejora)
  // Pasamos 'null' como texto para indicar que es loading animado
  const loadingId = agregarBurbuja(null, 'bot', true)

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
      agregarBurbuja('Lo siento, hubo un error procesando tu solicitud.', 'bot')
    } else {
      const botMsgId = agregarBurbuja(data.respuesta, 'bot')
      if (data.categoria || data.urgencia) {
        agregarEtiquetas(botMsgId, data)
      }
    }
  } catch (error) {
    console.error(error)
    eliminarBurbuja(loadingId)
    agregarBurbuja(
      'Error de conexión con el servidor. Inténtalo más tarde.',
      'bot'
    )
  }
}

// --- FUNCIÓN VISUAL DEL CHAT (Mejorada) ---
function agregarBurbuja(texto, tipo, esLoading = false) {
  const chatDiv = document.getElementById('chat-history')
  const rowDiv = document.createElement('div')

  // row-user (der) o row-bot (izq)
  rowDiv.className = `message-row row-${tipo}`
  const uniqueId = 'msg-' + Date.now()

  const msgDiv = document.createElement('div')
  msgDiv.className = `message ${tipo}-msg`

  if (esLoading) {
    // **MEJORA UX:** Animación de 3 puntos en vez de texto "Cargando"
    msgDiv.className += ' typing-indicator'
    msgDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      `
    rowDiv.id = uniqueId // Necesitamos ID para borrarlo luego
  } else {
    msgDiv.innerText = texto
  }

  rowDiv.appendChild(msgDiv)
  chatDiv.appendChild(rowDiv)

  // Auto-scroll suave
  setTimeout(() => {
    chatDiv.scrollTop = chatDiv.scrollHeight
  }, 10) // Pequeño delay para asegurar que el DOM pintó el elemento

  return uniqueId
}

function eliminarBurbuja(rowId) {
  const el = document.getElementById(rowId)
  if (el) el.remove()
}

function agregarEtiquetas(rowId, data) {
  // Ahora insertamos las etiquetas DENTRO de la burbuja, pero abajo
  const rowDiv = document.getElementById(rowId) // Esto selecciona la FILA, no la burbuja
  // Ojo: En mi lógica anterior devolví el ID del rowDiv en loading,
  // pero el ID lo genera agregarBurbuja.

  // Truco: buscamos el último mensaje bot si no tenemos ID exacto,
  // pero aquí asumimos que el rowId es correcto.
  if (!rowDiv) return

  const msgDiv = rowDiv.querySelector('.message')

  const tagsDiv = document.createElement('div')
  tagsDiv.style.marginTop = '8px'
  tagsDiv.style.display = 'flex'
  tagsDiv.style.gap = '6px'

  let html = ''
  if (data.categoria)
    html += `<span class="badge bg-cat">${data.categoria}</span>`
  if (data.urgencia)
    html += `<span class="badge bg-urg">${data.urgencia}</span>`

  tagsDiv.innerHTML = html
  msgDiv.appendChild(tagsDiv)

  const chatDiv = document.getElementById('chat-history')
  chatDiv.scrollTop = chatDiv.scrollHeight
}

// --- NAVEGACIÓN ---
function mostrarVista(vista) {
  document.getElementById('btn-chat').classList.remove('active')
  document.getElementById('btn-historial').classList.remove('active')

  if (vista === 'chat') {
    document.getElementById('btn-chat').classList.add('active')
    document.getElementById('chat-view').style.display = 'flex'
    document.getElementById('history-view').style.display = 'none'
  } else {
    document.getElementById('btn-historial').classList.add('active')
    document.getElementById('chat-view').style.display = 'none'
    document.getElementById('history-view').style.display = 'block'
  }
}

// --- HISTORIAL ---
async function cargarHistorial() {
  mostrarVista('historial')
  const filtro = document.getElementById('catFilter').value

  let url = `${API_URL}/consultas?user_id=${currentUserId}`
  if (filtro) url += `&categoria=${filtro}`

  try {
    const res = await fetch(url)
    const datos = await res.json()
    const tbody = document.querySelector('#historyTable tbody')
    tbody.innerHTML = ''

    if (datos.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="4" style="text-align:center; padding:30px; color:#94a3b8;">No se encontraron registros.</td></tr>'
      return
    }

    datos.forEach((item) => {
      // Truncar texto largo para que la tabla no se rompa
      const respCorta =
        item.respuesta.length > 50
          ? item.respuesta.substring(0, 50) + '...'
          : item.respuesta
      const catBadge = item.categoria
        ? `<span class="badge bg-cat">${item.categoria}</span>`
        : '<span style="color:#ccc">-</span>'

      const row = `<tr>
                <td>${item.fecha || 'Hoy'}</td>
                <td style="font-weight:500; color:#1e293b">${item.pregunta}</td>
                <td style="color:#64748b">${respCorta}</td>
                <td>${catBadge}</td>
            </tr>`
      tbody.innerHTML += row
    })
  } catch (err) {
    console.error(err)
    const tbody = document.querySelector('#historyTable tbody')
    tbody.innerHTML =
      '<tr><td colspan="4" style="color:salmon; text-align:center">Error de conexión</td></tr>'
  }
}
