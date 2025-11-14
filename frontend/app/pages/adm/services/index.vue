<!-- frontend/app/pages/adm/services/index.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'admin' })

import { ref, onMounted, computed, h } from 'vue'
import type { ColumnDef } from '@tanstack/vue-table'
import { useMyToast } from '~/composables/useMyToast'
import AdminTablePage from '~/components/AdminTablePage.vue'

const { $api } = useNuxtApp()
const toast = useMyToast()
const adminTitle = useAdminTitle()
const config = useRuntimeConfig()
const BACKEND_URL = config.public.apiBase

onMounted(() => {
  adminTitle.value = 'Service Management'
  load()
})

// --- table + pagination ---
const services = ref<any[]>([])
const pending = ref(false)
const page = ref(1)
const pageSize = 10
const total = ref(0)

const totalPages = computed(() =>
  Math.max(1, Math.ceil((total.value || services.value.length) / pageSize)),
)

function getLogoUrl(path?: string | null) {
  if (!path) return `${BACKEND_URL}/static/logos/default.png`
  if (path.startsWith('http')) return path
  return `${BACKEND_URL}${path}`
}

async function load() {
  pending.value = true
  try {
    const res: any = await $api('/adm/services', {
      query: { page: page.value, page_size: pageSize },
    })
    services.value = res.items ?? (Array.isArray(res) ? res : [])
    total.value = res.total ?? services.value.length
  } catch (err) {
    console.error('Failed to load services', err)
    toast.add({ title: 'Failed to load services', color: 'error' })
    services.value = []
    total.value = 0
  } finally {
    pending.value = false
  }
}

function go(p: number) {
  page.value = Math.max(1, p)
  load()
}

const openDetail = (id: number) => navigateTo(`/adm/services/${id}`)

// --- CREATE SERVICE MODAL + LOGO UPLOAD ---

const showCreate = ref(false)
const creating = ref(false)
const logoFile = ref<File | null>(null)

const newService = reactive({
  name: '',
  code: '',
  description: '',
})

function resetNewService() {
  newService.name = ''
  newService.code = ''
  newService.description = ''
  logoFile.value = null
}

function onLogoChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0] || null
  logoFile.value = file
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

async function createService() {
  if (!newService.name.trim() || !newService.code.trim()) {
    toast.add({ title: 'Name and Code are required', color: 'error' })
    return
  }

  creating.value = true
  try {
    let logo_url: string | null = null

    if (logoFile.value) {
      const form = new FormData()
      form.append('file', logoFile.value)
      const res: any = await $api('/adm/services/upload-logo', {
        method: 'POST',
        body: form,
      })
      logo_url = res.logo_url ?? null
    }

    const body: any = {
      name: newService.name.trim(),
      code: newService.code.trim(),
      description: newService.description || null,
    }
    if (logo_url) body.logo_url = logo_url

    await $api('/adm/services', { method: 'POST', body })
    toast.add({ title: 'Service created', color: 'success' })
    showCreate.value = false
    resetNewService()
    await load()
  } catch (err) {
    console.error(err)
    toast.add({ title: 'Create failed', color: 'error' })
  } finally {
    creating.value = false
  }
}

/* -----------------------------
    TABLE COLUMNS
------------------------------*/

type RowT = Record<string, any>

const columns: ColumnDef<RowT, any>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'logo_url',
    header: 'Logo',
    cell: ({ row }) => {
      const url = row.original.logo_url
      if (!url) {
        return h(
          'span',
          { class: 'text-xs text-gray-400' },
          'No logo',
        )
      }
      return h(
        'div',
        { class: 'flex items-center gap-2' },
        [
          h('img', {
            src: getLogoUrl(url),
            class:
              'w-8 h-8 rounded-full object-contain border border-gray-200',
            onError: (e: any) => (e.target.style.display = 'none'),
          }),
        ],
      )
    },
  },
  {
    accessorKey: 'name',
    header: 'Name',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'code',
    header: 'Code',
    cell: ({ getValue }) => String(getValue() ?? '-'),
  },
  {
    accessorKey: 'description',
    header: 'Description',
    cell: ({ getValue }) => {
      const val = String(getValue() ?? '')
      if (!val) return ''
      return val.length > 80 ? val.slice(0, 77) + '...' : val
    },
  },
]

/* Row click → go to edit page */
function onRowSelect(e: Event, row: any) {
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('a')) return
  const id = row.original.id
  if (id) openDetail(id)
}
</script>

<template>
  <AdminTablePage
    title="Service Management"
    :data="services"
    :columns="columns"
    :loading="pending"
    :page="page"
    :total-pages="totalPages"
    :on-row-select="onRowSelect"
    :disable-pagination="pending"
    @change-page="go"
  >
    <!-- top-right actions -->
    <template #actions>
      <UButton
        variant="solid"
        class="btn-dark"
        label="+ Create Service"
        @click="showCreate = true"
      />
    </template>

    <template #loading>
      <div class="p-6 text-center text-gray-500">
        Loading services…
      </div>
    </template>

    <template #empty>
      <div class="p-6 text-center text-gray-500">
        No services found.
      </div>
    </template>

    <template #summary>
      Page {{ page }} / {{ totalPages }}
    </template>
  </AdminTablePage>

  <!-- Create Service Modal -->
  <UModal v-model:open="showCreate" title="Create Service">
    <template #body>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-2">
        <UFormField label="Service Name">
          <UInput
            v-model="newService.name"
            color="neutral"
            placeholder="CDC Public Service"
            size="lg"
          />
        </UFormField>

        <UFormField label="Code">
          <UInput
            v-model="newService.code"
            color="neutral"
            placeholder="cdc"
            size="lg"
          />
        </UFormField>

        <UFormField label="Description" class="sm:col-span-2">
          <UInput
            v-model="newService.description"
            color="neutral"
            placeholder="Optional description"
            size="lg"
          />
        </UFormField>

        <UFormField label="Logo (image file)" class="sm:col-span-2">
          <UInput
            type="file"
            accept="image/*"
            color="neutral"
            size="lg"
            @change="onLogoChange"
          />
          <p class="mt-1 text-xs text-gray-500">
            PNG / JPG / WEBP – small square image works best.
          </p>
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-3 py-2 px-3">
        <UButton
          label="Cancel"
          color="neutral"
          variant="outline"
          @click="() => { showCreate = false; resetNewService() }"
        />
        <UButton
          label="Create"
          class="btn-dark"
          :loading="creating"
          :disabled="!newService.name || !newService.code"
          @click="createService"
        />
      </div>
    </template>
  </UModal>
</template>

<style scoped>
td {
  vertical-align: middle;
}
</style>
