<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import { clearAuth } from '../services/auth'
import ExperienceList from '../components/ExperienceList.vue'
import ReferenceList from '../components/ReferenceList.vue'

const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const roles = ref([])
const selectedPhoto = ref(null)
const photoInputKey = ref(0)
const selectedPhotoPreview = ref('')

const profile = ref({
  first_name: '',
  last_name: '',
  personal_photo_url: '',
  phone: '',
  city: '',
  role: null,
  roles: [],
  role_name: '',
  role_names: [],
  years_experience: 0,
  availability: '',
  bio: '',
  experiences: [],
  references: [],
})

const experienceForm = ref({
  company_name: '',
  role: '',
  start_date: '',
  end_date: '',
  is_current: false,
  description: '',
})

const referenceForm = ref({
  full_name: '',
  company: '',
  relation: '',
  phone: '',
  email: '',
  note: '',
})

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

async function fetchProfile() {
  loading.value = true
  try {
    const { data } = await api.get('/profile/')
    data.roles = Array.isArray(data.roles) && data.roles.length ? data.roles : (data.role ? [data.role] : [])
    profile.value = data
  } catch {
    error.value = 'No se pudo cargar tu perfil.'
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  try {
    const { data } = await api.get('/roles/')
    roles.value = data
  } catch {
    error.value = 'No se pudo cargar la lista de rubros.'
  }
}

async function saveProfile() {
  saving.value = true
  error.value = ''
  try {
    const payload = new FormData()
    payload.append('first_name', profile.value.first_name || '')
    payload.append('last_name', profile.value.last_name || '')
    payload.append('phone', profile.value.phone || '')
    payload.append('city', profile.value.city || '')
    const selectedRoles = Array.isArray(profile.value.roles) && profile.value.roles.length
      ? profile.value.roles
      : (profile.value.role ? [profile.value.role] : [])

    selectedRoles.forEach((roleId) => {
      payload.append('roles', String(roleId))
    })

    if (selectedRoles.length) {
      payload.append('role', String(selectedRoles[0]))
    }
    payload.append('years_experience', String(profile.value.years_experience ?? 0))
    payload.append('availability', profile.value.availability || '')
    payload.append('bio', profile.value.bio || '')
    if (selectedPhoto.value) {
      payload.append('personal_photo', selectedPhoto.value)
    }

    const { data } = await api.put('/profile/', payload)
    profile.value = data
    selectedPhoto.value = null
    photoInputKey.value += 1
  } catch {
    error.value = 'No se pudo guardar tu perfil.'
  } finally {
    saving.value = false
  }
}

function onPhotoChange(event) {
  const [file] = event.target.files || []
  selectedPhoto.value = file || null
}

function getPhotoPreviewUrl() {
  if (selectedPhotoPreview.value) {
    return selectedPhotoPreview.value
  }
  return profile.value.personal_photo_url
}

watch(selectedPhoto, (file) => {
  if (selectedPhotoPreview.value) {
    URL.revokeObjectURL(selectedPhotoPreview.value)
    selectedPhotoPreview.value = ''
  }

  if (file) {
    selectedPhotoPreview.value = URL.createObjectURL(file)
  }
})

onBeforeUnmount(() => {
  if (selectedPhotoPreview.value) {
    URL.revokeObjectURL(selectedPhotoPreview.value)
  }
})

async function addExperience() {
  error.value = ''
  try {
    await api.post('/experiences/', experienceForm.value)
    experienceForm.value = {
      company_name: '',
      role: '',
      start_date: '',
      end_date: '',
      is_current: false,
      description: '',
    }
    await fetchProfile()
  } catch {
    error.value = 'No se pudo agregar la experiencia.'
  }
}

async function deleteExperience(id) {
  try {
    await api.delete(`/experiences/${id}/`)
    await fetchProfile()
  } catch {
    error.value = 'No se pudo eliminar la experiencia.'
  }
}

async function addReference() {
  error.value = ''
  try {
    await api.post('/references/', referenceForm.value)
    referenceForm.value = {
      full_name: '',
      company: '',
      relation: '',
      phone: '',
      email: '',
      note: '',
    }
    await fetchProfile()
  } catch {
    error.value = 'No se pudo agregar la referencia.'
  }
}

async function deleteReference(id) {
  try {
    await api.delete(`/references/${id}/`)
    await fetchProfile()
  } catch {
    error.value = 'No se pudo eliminar la referencia.'
  }
}

function logout() {
  clearAuth()
  router.push('/auth')
}

onMounted(fetchProfile)
onMounted(fetchRoles)
</script>

<template>
  <section v-if="loading" class="panel">Cargando perfil...</section>

  <section v-else class="dashboard-grid">
    <article class="panel">
      <div class="header-inline">
        <h2>Mi perfil profesional</h2>
        <button class="secondary-btn" @click="logout">Cerrar sesión</button>
      </div>
      <form class="form-grid" @submit.prevent="saveProfile">
        <div class="profile-photo-block full-width">
          <img
            v-if="selectedPhoto || profile.personal_photo_url"
            :src="getPhotoPreviewUrl()"
            alt="Foto personal del trabajador"
            class="profile-photo-preview"
          />
          <label class="full-width">
            Fotografía personal
            <input
              :key="photoInputKey"
              type="file"
              accept="image/*"
              @change="onPhotoChange"
            />
          </label>
          <small class="field-hint">Formato recomendado: JPG o PNG, imagen vertical, hasta 5 MB.</small>
        </div>

        <label>
          Nombre
          <input v-model="profile.first_name" required />
        </label>
        <label>
          Apellido
          <input v-model="profile.last_name" required />
        </label>
        <label>
          Teléfono
          <input v-model="profile.phone" required />
        </label>
        <label>
          Ciudad
          <input v-model="profile.city" required />
        </label>
        <div class="full-width roles-field">
          <span>Rubros</span>
          <div class="roles-checkboxes" role="group" aria-label="Rubros disponibles">
            <label v-for="roleItem in roles" :key="roleItem.id" class="checkbox-label role-checkbox">
              <input v-model="profile.roles" type="checkbox" :value="roleItem.id" />
              {{ formatRubroLabel(roleItem.name) }}
            </label>
          </div>
          <small class="field-hint">Podés seleccionar uno o varios rubros.</small>
        </div>
        <label>
          Años de experiencia
          <input v-model.number="profile.years_experience" type="number" min="0" required />
        </label>
        <label>
          Disponibilidad
          <input v-model="profile.availability" placeholder="Full time, turno noche, fines de semana..." />
        </label>
        <label class="full-width">
          Presentación profesional
          <textarea v-model="profile.bio" rows="4" placeholder="Contá tu recorrido y fortalezas en gastronomía"></textarea>
        </label>
        <button class="primary-btn" type="submit" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar perfil' }}</button>
      </form>
    </article>

    <article class="panel">
      <h2>Nueva experiencia</h2>
      <form class="form-grid" @submit.prevent="addExperience">
        <label>
          Empresa
          <input v-model="experienceForm.company_name" required />
        </label>
        <label>
          Rol
          <input v-model="experienceForm.role" required />
        </label>
        <label>
          Fecha inicio
          <input v-model="experienceForm.start_date" type="date" required />
        </label>
        <label>
          Fecha fin
          <input v-model="experienceForm.end_date" type="date" :disabled="experienceForm.is_current" />
        </label>
        <label class="checkbox-label">
          <input v-model="experienceForm.is_current" type="checkbox" />
          Trabajo actual
        </label>
        <label class="full-width">
          Descripción
          <textarea v-model="experienceForm.description" rows="3"></textarea>
        </label>
        <button class="primary-btn" type="submit">Agregar experiencia</button>
      </form>
      <ExperienceList :experiences="profile.experiences" @delete="deleteExperience" />
    </article>

    <article class="panel">
      <h2>Nueva referencia</h2>
      <form class="form-grid" @submit.prevent="addReference">
        <label>
          Nombre
          <input v-model="referenceForm.full_name" required />
        </label>
        <label>
          Empresa
          <input v-model="referenceForm.company" />
        </label>
        <label>
          Relación
          <input v-model="referenceForm.relation" placeholder="Ex jefe, supervisor, compañero" required />
        </label>
        <label>
          Teléfono
          <input v-model="referenceForm.phone" />
        </label>
        <label>
          Email
          <input v-model="referenceForm.email" type="email" />
        </label>
        <label class="full-width">
          Nota
          <textarea v-model="referenceForm.note" rows="3"></textarea>
        </label>
        <button class="primary-btn" type="submit">Agregar referencia</button>
      </form>
      <ReferenceList :references="profile.references" @delete="deleteReference" />
    </article>

    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>
