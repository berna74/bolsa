<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const loading = ref(true)
const error = ref('')
const groups = ref([])
const route = useRoute()
const router = useRouter()
const selectedRubro = ref(null)
const selectedCity = ref('all')

const workerSearch = computed({
  get() {
    return typeof route.query.q === 'string' ? route.query.q : ''
  },
  set(value) {
    const nextValue = value.trim()
    const nextQuery = { ...route.query }

    if (nextValue) {
      nextQuery.q = nextValue
    } else {
      delete nextQuery.q
    }

    router.replace({ path: route.path, query: nextQuery })
  },
})

const searchTerm = computed(() => {
  return typeof route.query.q === 'string' ? route.query.q.trim().toLowerCase() : ''
})

const sortedGroups = computed(() => {
  return [...groups.value].sort((a, b) => {
    const countDiff = (b.workers?.length || 0) - (a.workers?.length || 0)
    if (countDiff !== 0) {
      return countDiff
    }
    return a.rubro.localeCompare(b.rubro)
  })
})

const availableCities = computed(() => {
  const cities = new Set()
  for (const group of groups.value) {
    for (const worker of group.workers || []) {
      const city = (worker.city || '').trim()
      if (city) {
        cities.add(city)
      }
    }
  }
  return [...cities].sort((a, b) => a.localeCompare(b, 'es'))
})

const filteredGroups = computed(() => {
  let groups = sortedGroups.value
  
  // Filtrar por rubro seleccionado
  if (selectedRubro.value) {
    groups = groups.filter((g) => g.rubro === selectedRubro.value)
  }
  
  if (selectedCity.value !== 'all') {
    groups = groups
      .map((group) => ({
        ...group,
        workers: group.workers.filter((worker) => (worker.city || '').trim() === selectedCity.value),
      }))
      .filter((group) => group.workers.length > 0)
  }

  // Filtrar por búsqueda
  const term = searchTerm.value
  if (!term) {
    return groups.map((group) => ({
      ...group,
      total: group.workers.length,
    }))
  }

  return groups
    .map((group) => {
      const workers = group.workers.filter((worker) => worker.full_name.toLowerCase().includes(term))
      return {
        ...group,
        workers,
        total: group.workers.length,
      }
    })
    .filter((group) => group.workers.length > 0)
})

const HOME_PREVIEW = 5

const previewGroups = computed(() =>
  filteredGroups.value.map((group) => ({
    ...group,
    workers: group.workers.slice(0, HOME_PREVIEW),
  }))
)

function rubroAnchor(rubro) {
  return `rubro-${rubro.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')}`
}

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

async function fetchWorkers() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/public/workers-by-role/')
    groups.value = data
  } catch {
    error.value = 'No se pudo cargar el listado de trabajadores.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchWorkers)
</script>

<template>
  <section class="panel home-panel">
    <div class="home-header">
      <h2>Trabajadores registrados por rubro</h2>
      <label class="home-search-shell" for="worker-search-input">
        <span class="home-search-prefix">Buscar trabajador...</span>
        <input
          id="worker-search-input"
          v-model="workerSearch"
          type="search"
          placeholder="Ej: Juan Perez"
          class="home-search-input home-search-input-inline"
        />
      </label>
      <select v-model="selectedRubro" class="rubros-select" aria-label="Filtrar por rubro">
        <option :value="null">Todos los rubros</option>
        <option v-for="group in sortedGroups" :key="group.rubro" :value="group.rubro">
          {{ formatRubroLabel(group.rubro) }} ({{ group.workers.length }})
        </option>
      </select>
      <select v-model="selectedCity" class="rubros-select" aria-label="Filtrar por ciudad">
        <option value="all">Todas las ciudades</option>
        <option v-for="city in availableCities" :key="city" :value="city">
          {{ city }}
        </option>
      </select>
    </div>

    <p v-if="loading">Cargando trabajadores...</p>
    <p v-else-if="error" class="error-text">{{ error }}</p>

    <template v-else>
      <p v-if="!filteredGroups.length" class="empty-state">No hay trabajadores que coincidan con la búsqueda.</p>

      <div class="role-grid">
        <article v-for="group in previewGroups" :id="rubroAnchor(group.rubro)" :key="group.rubro" class="role-card">
          <h3>
            <router-link class="role-link" :to="`/rubro/${rubroSlug(group.rubro)}`">
              {{ formatRubroLabel(group.rubro) }} ({{ group.total }})
            </router-link>
          </h3>
          <ul class="worker-list">
            <li v-for="worker in group.workers" :key="worker.id">
              <div class="worker-row">
                <img
                  v-if="worker.personal_photo_url"
                  :src="worker.personal_photo_url"
                  :alt="`Foto de ${worker.full_name}`"
                  class="worker-photo"
                />
                <div v-else class="worker-photo worker-photo-placeholder" aria-hidden="true">
                  {{ worker.full_name.charAt(0).toUpperCase() }}
                </div>
                <div class="worker-meta">
                  <router-link class="worker-link" :to="`/trabajador/${worker.id}`">
                    <strong>{{ worker.full_name }}</strong>
                  </router-link>
                  <span>{{ worker.city || 'Ciudad no indicada' }}</span>
                  <span>{{ worker.years_experience }} años de experiencia</span>
                  <span v-if="worker.availability">Disponibilidad: {{ worker.availability }}</span>
                  <div class="worker-actions">
                    <a
                      v-if="whatsappLink(worker.phone, worker.full_name)"
                      :href="whatsappLink(worker.phone, worker.full_name)"
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
                      v-if="emailLink(worker.email, worker.full_name)"
                      :href="emailLink(worker.email, worker.full_name)"
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
            </li>
          </ul>
          <router-link
            v-if="group.total > 5"
            class="role-card-more"
            :to="`/rubro/${rubroSlug(group.rubro)}`"
          >
            Ver los {{ group.total - 5 }} restantes &rarr;
          </router-link>
        </article>
      </div>
    </template>
  </section>
</template>
