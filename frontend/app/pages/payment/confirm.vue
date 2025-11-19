<!-- src/pages/payment/confirm.vue -->
<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
    <!-- Header -->
    <div class="relative flex items-center justify-center w-full max-w-lg mb-8">
      <button
        @click="navigateTo('/payment/invoice')"
        class="absolute left-4 p-2 bg-white rounded-full shadow hover:bg-gray-100 transition"
        aria-label="Back to invoice"
      >
        <ArrowLeft class="w-5 h-5 text-gray-700" />
      </button>
      <h2 class="text-xl font-semibold text-gray-800 text-center">
        Confirm Payment
      </h2>
    </div>

    <!-- Confirmation Card -->
    <div
      class="bg-white rounded-2xl shadow w-full max-w-lg p-6 space-y-5 text-center border border-gray-100"
    >
      <!-- Service Logo -->
      <div v-if="payment?.service?.logo_url" class="flex justify-center mb-3">
        <img
          :src="getLogoUrl(payment.service.logo_url)"
          alt="Service Logo"
          class="w-20 h-20 object-contain rounded-full"
        />
      </div>

      <!-- Service Name -->
      <h3 class="text-lg font-semibold text-gray-800">
        Bill to {{ payment?.service?.name || 'Service' }}
      </h3>

      <!-- Bill Info -->
      <div class="text-left text-sm space-y-4">
        <div class="flex justify-between">
          <span class="text-gray-500">From Account</span>
          <span class="font-medium text-gray-800">{{
            payment?.from_account?.number || '-'
          }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Customer Name</span>
          <span class="font-medium text-gray-800">{{
            payment?.customer_name || '-'
          }}</span>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">CDC. Ref. No.</span>
          <span class="font-medium text-gray-800">{{
            payment?.reference_number || '-'
          }}</span>
        </div>

        <div class="dotted-divider"></div>

        <div class="flex justify-between items-start">
          <span class="text-gray-500">Amount</span>
          <div class="text-right">
            <p class="font-medium text-gray-800">
              {{ formatCurrency(payment?.invoice_amount, payment?.invoice_currency) }}
            </p>
            <p
              v-if="payment?.invoice_currency === 'KHR'"
              class="text-xs text-gray-500"
            >
              ≈ {{ formatCurrency(convertToUSD(payment?.invoice_amount), 'USD') }}
            </p>
          </div>
        </div>

        <div class="flex justify-between">
          <span class="text-gray-500">Fee</span>
          <span class="font-medium text-gray-800">
            {{ formatCurrency(payment?.fee, payment?.currency || payment?.invoice_currency || 'USD') }}
          </span>
        </div>
        <div class="dotted-divider"></div>

        <div class="flex justify-between text-base font-semibold">
          <span>Total Amount</span>
          <div class="text-right">
            <p>
              {{ formatCurrency(payment?.total_amount, payment?.currency || payment?.invoice_currency || 'USD') }}
            </p>
            <p
              v-if="payment?.currency === 'KHR'"
              class="text-xs text-gray-500"
            >
              ≈ {{ formatCurrency(convertToUSD(payment?.total_amount), 'USD') }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- PIN Input -->
    <div
      class="bg-white rounded-2xl shadow w-full max-w-lg p-6 text-center mt-8 border border-gray-100"
    >
      <p class="text-sm text-gray-600 mb-4">
        Enter your 4-digit PIN to confirm payment
      </p>

      <div class="flex justify-center space-x-3 mb-6" @paste.prevent="handlePaste">
        <input
          v-for="(n, idx) in 4"
          :key="idx"
          :ref="setPinInputRef"
          v-model="pin[idx]"
          inputmode="numeric"
          pattern="[0-9]*"
          maxlength="1"
          autocomplete="one-time-code"
          type="password"
          :aria-label="`PIN digit ${idx + 1}`"
          class="w-12 h-12 text-center border border-gray-300 rounded-lg text-lg font-semibold focus:ring-2 focus:ring-blue-500 focus:outline-none"
          @input="handleInput(idx, $event)"
          @keydown="handleKeyDown(idx, $event)"
        />
      </div>

      <button
        :disabled="!isPinComplete || confirming"
        @click="confirmPayment"
        class="w-full py-2 bg-gradient-to-r from-gray-800 to-gray-900 text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition"
        aria-disabled="!isPinComplete || confirming"
      >
        <span v-if="confirming">Confirming...</span>
        <span v-else>Confirm Payment</span>
      </button>

      <p v-if="error" class="text-red-600 text-sm mt-3">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next';
import { formatCurrency, convertToUSD } from '~/utils/helpers';
import { useMyToast } from '~/composables/useMyToast';
import { ref, watch } from 'vue';

const { $api } = useNuxtApp();
const payment = useState<any>('payment');
const pin = ref<string[]>(['', '', '', '']);
const pinInputs = ref<HTMLInputElement[]>([]);
const confirming = ref(false);
const error = ref('');
const toast = useMyToast();
const config = useRuntimeConfig();
const BACKEND_URL = config.public.apiBase;

const getLogoUrl = (path: string) =>
  !path
    ? `${BACKEND_URL}/static/logos/default.svg`
    : path.startsWith('http')
    ? path
    : `${BACKEND_URL}${path}`;

/** helper for template ref array */
function setPinInputRef(el: HTMLInputElement | null) {
  if (!el) return;
  // maintain order by index presence (Vue pushes in render order)
  pinInputs.value.push(el);
}

/** Move focus to the element at index (if exists) */
function focusAt(index: number) {
  const el = pinInputs.value[index];
  if (el) el.focus();
}

/** Input handler: accept only digits, fill model, move focus forward */
const handleInput = (index: number, e: Event) => {
  error.value = '';
  const el = e.target as HTMLInputElement;
  let val = el.value || '';
  // keep digits only
  val = val.replace(/\D/g, '');
  // only keep first char (since maxlength=1)
  if (val.length > 1) val = val.slice(0, 1);
  pin.value[index] = val;
  // ensure input displays the filtered value (helps with pasted non-digits)
  el.value = val;
  if (val && index < 3) {
    focusAt(index + 1);
  }
  // if user typed in last digit, blur to hide keyboard on mobile
  if (index === 3 && val) {
    el.blur();
  }
};

/** Keydown handler: backspace moves focus back when empty */
const handleKeyDown = (index: number, e: KeyboardEvent) => {
  if (e.key === 'Backspace') {
    const el = e.target as HTMLInputElement;
    if (!el.value && index > 0) {
      // move focus back and clear previous
      focusAt(index - 1);
      pin.value[index - 1] = '';
    } else {
      // clear current value (default backspace behavior)
      pin.value[index] = '';
    }
  } else if (e.key === 'ArrowLeft' && index > 0) {
    focusAt(index - 1);
  } else if (e.key === 'ArrowRight' && index < 3) {
    focusAt(index + 1);
  } else if (e.key && /\d/.test(e.key) && (e.target as HTMLInputElement).value && index < 3) {
    // If pressing a digit when current already filled, write and advance:
    // (This is optional fallback; main flow handled in input event)
    focusAt(index + 1);
  }
};

/** Paste handler: extract digits and fill all boxes */
function handlePaste(e: ClipboardEvent) {
  error.value = '';
  const text = (e.clipboardData?.getData('text') || '').replace(/\D/g, '');
  if (!text) return;
  const digits = text.slice(0, 4).split('');
  for (let i = 0; i < 4; i++) {
    pin.value[i] = digits[i] || '';
    if (pinInputs.value[i]) pinInputs.value[i].value = pin.value[i] || '';
  }
  // focus last filled or next
  const nextIndex = Math.min(digits.length, 3);
  focusAt(nextIndex);
}

/** computed-ish helpers */
const isPinComplete = computed(() => pin.value.join('').length === 4);

/** Auto-focus first input when page mounts */
onMounted(() => {
  // small timeout to ensure refs populated
  setTimeout(() => focusAt(0), 50);
});

/** Watch payment change: clear pin & errors when new payment loaded */
watch(payment, () => {
  pin.value = ['', '', '', ''];
  error.value = '';
  pinInputs.value = []; // will be repopulated by setPinInputRef on render
});

/** Confirm payment — send both body and query pin for compatibility */
const confirmPayment = async () => {
  if (!payment.value?.id) {
    toast.show('Invalid payment session. Please start again.', 'error');
    navigateTo('/payment/invoice');
    return;
  }
  if (!isPinComplete.value) {
    error.value = 'Please enter 4-digit PIN';
    return;
  }

  confirming.value = true;
  try {
    const code = pin.value.join('');
    // try sending as body first, also include query param for backward compatibility
    const res = await $api(
      `/payments/${payment.value.id}/confirm?pin=${encodeURIComponent(code)}`,
      {
        method: 'POST',
        body: { pin: code },
      }
    );
    payment.value = { ...payment.value, ...res, status: 'confirmed' };
    toast.show('Payment confirmed successfully!', 'success');
    navigateTo('/payment/success');
  } catch (err: any) {
    // normalize error message
    const msg =
      err?.response?._data?.detail ||
      err?.response?._data?.message ||
      err?.data?.detail ||
      err?.message ||
      'Failed to confirm payment.';
    error.value = String(msg);
    toast.show(error.value, 'error');
    // clear pin inputs so user can retry
    pin.value = ['', '', '', ''];
    pinInputs.value.forEach((el) => { if (el) el.value = ''; });
    // focus first
    setTimeout(() => focusAt(0), 50);
  } finally {
    confirming.value = false;
  }
};
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
