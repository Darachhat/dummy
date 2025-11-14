<!-- components/AdminTablePage.vue -->
<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'

type RowT = Record<string, any>

const props = defineProps<{
  title: string
  data: RowT[]
  columns: ColumnDef<RowT, any>[] | any
  loading?: boolean
  page: number
  totalPages: number
  /** UTable onSelect handler */
  onRowSelect?: (e: Event, row: any) => void
  /** Disable pagination buttons while loading */
  disablePagination?: boolean
}>()

const emit = defineEmits<{
  (e: 'change-page', value: number): void
}>()

function changePage(newPage: number) {
  if (newPage < 1 || newPage > props.totalPages) return
  emit('change-page', newPage)
}
</script>

<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-3">
      <h2 class="text-2xl hidden md:block font-bold">
        {{ title }}
      </h2>
      <div class="flex flex-wrap items-center gap-3">
        <!-- actions slot (e.g. + Create User) -->
        <slot name="actions" />
      </div>
    </div>

    <!-- TABLE CARD -->
    <UCard class="shadow-sm border rounded-xl overflow-hidden">
      <UTable
        :data="data"
        :columns="columns"
        :loading="loading"
        :onSelect="onRowSelect"
        class="min-w-full"
      >
        <!-- forward all custom column slots like created_at-cell, status-cell, etc. -->
        <template
          v-for="(_, name) in $slots"
          v-if="name.endsWith('-cell')"
          #[name]="slotProps"
        >
          <slot :name="name" v-bind="slotProps" />
        </template>

        <template #loading>
          <slot name="loading">
            <div class="p-6 text-center text-gray-500">
              Loading…
            </div>
          </slot>
        </template>

        <template #empty>
          <slot name="empty">
            <div class="p-6 text-center text-gray-500">
              No data found.
            </div>
          </slot>
        </template>
      </UTable>

      <template #footer>
        <div class="flex flex-col md:flex-row md:items-center md:justify-between p-3 text-sm text-gray-600 gap-3">
          <!-- summary slot (override if needed) -->
          <div>
            <slot name="summary">
              Page {{ page }} / {{ totalPages }}
            </slot>
          </div>

          <div class="flex gap-2">
            <UButton
              label="Prev"
              color="neutral"
              variant="outline"
              :disabled="page <= 1 || loading || disablePagination"
              @click="changePage(page - 1)"
            />
            <UButton
              label="Next"
              class="btn-dark"
              :disabled="page >= totalPages || loading || disablePagination"
              @click="changePage(page + 1)"
            />
          </div>
        </div>
      </template>
    </UCard>
  </div>
</template>
