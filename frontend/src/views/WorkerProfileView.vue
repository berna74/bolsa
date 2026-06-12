<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const groups = ref([])

function rubroSlug(rubro) {
  return rubro
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function formatRubroLabel(rubro) {
  const value = (rubro || '').trim()
  if (!value) {
    return ''
  }

  if (/os$/i.test(value)) {
    return `${value}/as`
  }

  if (/as$/i.test(value)) {
    return `${value}/os`
  }

  if (/o$/i.test(value)) {
    return `${value.slice(0, -1)}os/as`
  }

  if (/a$/i.test(value)) {
    return `${value.slice(0, -1)}as/os`
  }

  if (/s$/i.test(value)) {
    return value
  }

  if (/[aeiouaeiou]$/i.test(value)) {
    return `${value}s`
  }

  return `${value}es`
}

function sanitizePhone(phone) {
  return (phone || '').replace(/[^\d+]/g, '')
}

function whatsappLink(phone, name) {
  const cleanPhone = sanitizePhone(phone)
  if (!cleanPhone) {
    return ''
  }
  const message = encodeURIComponent(`Hola ${name}, vi tu perfil en ConTodoGusto y me gustaría contactarte.`)
  return `https://wa.me/${cleanPhone}?text=${message}`
}

function emailLink(email, name) {
  if (!email) {
    return ''
  }
  const subject = encodeURIComponent('Contacto laboral desde ConTodoGusto')
  const body = encodeURIComponent(`Hola ${name}, vi tu perfil y me gustaría conversar sobre una oportunidad laboral.`)
  return `mailto:${email}?subject=${subject}&body=${body}`
}

const workerData = computed(() => {
  const workerId = Number(route.params.id)
  for (const group of groups.value) {
    const worker = group.workers.find((item) => item.id === workerId)
    if (worker) {
      return { ...worker, rubro: group.rubro }
    }
  }
  return null
})

async function fetchWorkersByRole() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/public/workers-by-role/')
    groups.value = data
  } catch {
    error.value = 'No se pudo cargar el perfil del trabajador.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchWorkersByRole)
</script>

<template>
  <section class="panel detail-panel">
    <p v-if="loading">Cargando perfil...</p>
    <p v-else-if="error" class="error-text">{{ error }}</p>

    <template v-else-if="workerData">
      <div class="worker-profile-header">
        <img
          v-if="workerData.personal_photo_url"
          :src="workerData.personal_photo_url"
          :alt="`Foto de ${workerData.full_name}`"
          class="worker-photo worker-photo-lg"
        />
        <div v-else class="worker-photo worker-photo-lg worker-photo-placeholder" aria-hidden="true">
          {{ workerData.full_name.charAt(0).toUpperCase() }}
        </div>

        <div class="worker-profile-meta">
          <h2>{{ workerData.full_name }}</h2>
          <p><strong>Rubro:</strong> {{ formatRubroLabel(workerData.rubro) }}</p>
            <p v-if="workerData.rubros?.length"><strong>También se registra en:</strong> {{ workerData.rubros.map(formatRubroLabel).join(', ') }}</p>
          <p><strong>Ciudad:</strong> {{ workerData.city || 'Ciudad no indicada' }}</p>
          <p><strong>Experiencia:</strong> {{ workerData.years_experience }} años</p>
          <p v-if="workerData.availability"><strong>Disponibilidad:</strong> {{ workerData.availability }}</p>
          <div class="worker-actions worker-actions-detail">
            <a
              v-if="whatsappLink(workerData.phone, workerData.full_name)"
              :href="whatsappLink(workerData.phone, workerData.full_name)"
              target="_blank"
              rel="noopener noreferrer"
              class="contact-btn"
              aria-label="Contactar por WhatsApp"
              title="WhatsApp"
            >
              <svg class="btn-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M12 3a8.5 8.5 0 00-7.302 12.87L4 21l5.305-1.659A8.5 8.5 0 1012 3z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <path
                  d="M9.2 9.8c.2-.4.5-.4.7-.4h.6c.2 0 .4.1.5.3l.5 1.1c.1.2 0 .4-.1.5l-.4.6c.5.9 1.2 1.5 2 2l.6-.4c.2-.1.4-.2.6-.1l1.1.5c.2.1.3.3.3.5v.6c0 .2 0 .5-.4.7-.7.3-1.5.3-2.2 0-2-.8-3.6-2.4-4.4-4.4-.3-.7-.3-1.5 0-2.2z"
                  fill="currentColor"
                />
              </svg>
            </a>
            <a
              v-if="emailLink(workerData.email, workerData.full_name)"
              :href="emailLink(workerData.email, workerData.full_name)"
              class="contact-btn"
              aria-label="Contactar por Email"
              title="Email"
            >
              <svg class="btn-icon" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M4 6h16v12H4z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linejoin="round"
                />
                <path
                  d="M4 7l8 6 8-6"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </a>
          </div>
        </div>
      </div>

      <section v-if="workerData.bio" class="worker-bio-block">
        <h3>Presentación profesional</h3>
        <p>{{ workerData.bio }}</p>
      </section>

      <div class="detail-actions">
        <router-link class="secondary-btn" :to="`/rubro/${rubroSlug(workerData.rubro)}`">
          Ver más trabajadores de este rubro
        </router-link>
        <router-link class="secondary-btn" to="/">Volver al inicio</router-link>
      </div>
    </template>

    <template v-else>
      <h2>Perfil no encontrado</h2>
      <p>El trabajador no existe o ya no está publicado.</p>
      <router-link class="secondary-btn" to="/">Volver al inicio</router-link>
    </template>
  </section>
</template>
