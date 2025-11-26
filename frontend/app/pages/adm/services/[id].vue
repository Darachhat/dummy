<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMyToast } from '~/composables/useMyToast'
import LoadingSpinner from '~/components/ui/LoadingSpinner.vue'


const route = useRoute()
const router = useRouter()
const toast = useMyToast()
const { $api } = useNuxtApp()

const adminTitle = useAdminTitle()
adminTitle.value = 'Edit Service'

const service = ref<any | null>(null)
const loading = ref(false)
const saving = ref(false)

// logo upload state
const logoFile = ref<File | null>(null)
const logoPreview = ref<string | null>(null)

const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

const getLogoUrl = (path?: string | null) => {
  if (!path) return `${BACKEND_URL}/static/logos/default.svg`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

async function loadService() {
  const id = route.params.id
  if (!id) {
    toast.add({ title: 'Missing service id', color: 'error' })
    return
  }

  loading.value = true
  try {
    const res = await $api(`/adm/services/${id}`)
    service.value = res
    logoPreview.value = getLogoUrl(service.value.logo_url)
  } catch (err) {
    console.error('Failed to load service', err)
    toast.add({ title: 'Failed to load service', color: 'error' })
  } finally {
    loading.value = false
  }
}

function onLogoChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0] || null
  logoFile.value = file
  if (file) {
    logoPreview.value = URL.createObjectURL(file)
  } else {
    logoPreview.value = getLogoUrl(service.value?.logo_url)
  }
}

async function uploadLogoIfAny(): Promise<string | null> {
  if (!logoFile.value) return null

  const form = new FormData()
  form.append('file', logoFile.value)

  const res: any = await $api('/adm/services/upload-logo', {
    method: 'POST',
    body: form,
  })
  return res.logo_url ?? null
}

async function saveService() {
  if (!service.value) return

  const id = service.value.id
  if (!id) {
    toast.add({ title: 'Invalid service', color: 'error' })
    return
  }
  if (!service.value.name || !service.value.code) {
    toast.add({ title: 'Name and Code are required', color: 'error' })
    return
  }

  saving.value = true
  try {
    let logo_url = service.value.logo_url ?? null
    if (logoFile.value) {
      try {
        const uploaded = await uploadLogoIfAny()
        if (uploaded) logo_url = uploaded
      } catch (err) {
        console.error('Logo upload failed', err)
        toast.add({ title: 'Logo upload failed', color: 'error' })
      }
    }

    await $api(`/adm/services/${id}`, {
      method: 'PUT',
      body: {
        name: String(service.value.name).trim(),
        code: String(service.value.code).trim(),
        logo_url,
        description: service.value.description || null,
      },
    })
    toast.add({ title: 'Service updated', color: 'success' })
    router.push('/adm/services')
  } catch (err) {
    console.error('Update service failed', err)
    toast.add({ title: 'Update service failed', color: 'error' })
  } finally {
    saving.value = false
  }
}

async function deleteService() {
  if (!service.value?.id) return
  if (!confirm(`Delete service "${service.value.name}"?`)) return

  saving.value = true
  try {
    await $api(`/adm/services/${service.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Service deleted', color: 'success' })
    router.push('/adm/services')
  } catch (err) {
    console.error('Delete service failed', err)
    toast.add({ title: 'Delete service failed', color: 'error' })
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/adm/services')
}

onMounted(loadService)
</script>

<template>
  <div class="p-6 max-w-8xl mx-auto space-y-6">
    <!-- Header -->
   <div
  class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 py-2 border-b border-gray-100"
>
  <!-- Left: Back + Title -->
  <div class="flex items-center gap-4">
    <UButton
      color="neutral"
      variant="ghost"
      icon="i-lucide-arrow-left"
      class="rounded-full h-10 w-10 flex items-center justify-center"
      @click="goBack"
    />

    <div>
      <h1 class="text-xl font-semibold text-gray-800">Edit Service</h1>
      <p class="text-sm text-gray-500">
        Manage service details and branding.
      </p>
    </div>
  </div>

  <!-- Right: ID + Delete -->
  <div class="flex items-center gap-3">
    <span
      v-if="service?.id"
      class="inline-flex items-center rounded-full bg-gray-100 text-gray-600 px-3 py-1 text-xs font-medium border border-gray-200"
    >
      Service ID: <span class="ml-1 font-semibold">{{ service.id }}</span>
    </span>

    <UButton
      color="red"
      variant="solid"
      icon="i-lucide-trash"
      :loading="saving"
      class="px-4"
      @click="deleteService"
    >
      Delete
    </UButton>
  </div>
</div>


    <!-- Content -->
    <UCard class="shadow-sm border rounded-2xl overflow-hidden">
     <div v-if="loading" class="p-8 text-center text-gray-500">
    <LoadingSpinner />
    <div class="mt-3">Loading service…</div>
  </div>

      <div
        v-else-if="service"
        class="grid gap-8 p-4 md:p-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1.2fr)]"
      >
        <!-- Form -->
        <div class="space-y-6">
          <div class="space-y-1">
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Service details
            </p>
            <p class="text-xs text-gray-400">
              Basic info customers will see when choosing this service.
            </p>
          </div>

          <div class="space-y-4">
            <UFormField label="Name" required>
              <UInput
                v-model="service.name"
                color="neutral"
                placeholder="Enter service name"
                size="lg"
              />
            </UFormField>

            <UFormField label="Code" required>
              <UInput
                v-model="service.code"
                color="neutral"
                placeholder="Short code (e.g. cdc)"
                size="lg"
              />
            </UFormField>

            <UFormField label="Description">
              <UTextarea
                v-model="service.description"
                color="neutral"
                :rows="3"
                placeholder="Short description of this service"
              />
            </UFormField>
          </div>

          <div class="pt-2 space-y-4 border-t border-dashed border-gray-200">

            <UFormField label="Change Logo (image file)">
              <UInput
                type="file"
                accept="image/*"
                color="neutral"
                size="lg"
                @change="onLogoChange"
              />
              <p class="mt-1 text-xs text-gray-500">
                PNG / JPG / WEBP — square image recommended. Leave empty to keep
                the existing logo.
              </p>
            </UFormField>
          </div>
        </div>

        <!-- Preview -->
        <div class="space-y-4">
          <div class="space-y-1">
            <p class="text-xs font-semibold tracking-wide text-gray-500 uppercase">
              Preview
            </p>
            <p class="text-xs text-gray-400">
              This is how the service may appear in the payment UI.
            </p>
          </div>

          <div class="preview-card">
            <div
              class="w-14 h-14 rounded-full bg-white/80 border flex items-center justify-center overflow-hidden shadow-sm"
            >
              <img
                :src="logoPreview || getLogoUrl(service.logo_url)"
                alt="Service Logo"
                class="w-full h-full object-contain"
              />
            </div>

            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 truncate">
                {{ service.name || 'Service name' }}
              </p>
              <p class="text-xs text-gray-500 uppercase tracking-wide">
                CODE: {{ (service.code || '---').toString().toUpperCase() }}
              </p>
              <p class="text-xs text-gray-400 mt-1 line-clamp-2">
                {{ service.description || 'Description will appear here.' }}
              </p>
            </div>
          </div>

          <div class="rounded-xl bg-gray-50 px-4 py-3 text-xs text-gray-500">
            <p class="font-medium text-gray-600 mb-1">
              Technical details
            </p>
            <p class="flex justify-between">
              <span>Logo path</span>
              <span class="font-mono truncate max-w-[180px] text-right">
                {{ service.logo_url || '(auto from upload)' }}
              </span>
            </p>
          </div>
        </div>
      </div>

      <div v-else class="p-8 text-center text-gray-500">
        Service not found.
      </div>

      <template #footer>
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between py-3 px-4">
          <p class="text-xs text-gray-400">
            Changes are applied immediately after saving.
          </p>
          <div class="flex justify-end gap-3">
            <UButton
              label="Cancel"
              color="neutral"
              variant="outline"
              @click="goBack"
            />
            <UButton
              label="Save Changes"
              class="btn-dark"
              :loading="saving"
              :disabled="!service?.name || !service?.code"
              @click="saveService"
            />
          </div>
        </div>
      </template>
    </UCard>
  </div>
</template>

