<template>
  <q-input
    ref="passwordRef"
    square
    filled
    lazy-rules
    :rules="myRules"
    :type="isPwd ? 'password' : 'text'"
  >
    <template v-slot:append>
      <q-icon
        :name="isPwd ? 'visibility_off' : 'visibility'"
        class="cursor-pointer"
        @click="isPwd = !isPwd"
      />
    </template>
  </q-input>
</template>

<script>
import { defineComponent, ref, computed } from 'vue';
import { password_rules } from 'src/core/validation';

export default defineComponent({
  props: {
    validate: {
      type: Boolean,
      default: false,
    },

    rules: {
      type: any,
      default: [(val) => (val && val.length > 0) || 'Password cannot be empty'],
    },
  },

  setup(props) {
    const isPwd = ref(true);

    const myRules = computed(() => {
      if (props.validate) {
        return [...password_rules];
      } else {
        return props.rules;
      }
    });

    return {
      password_rules,
      props,
      isPwd,
      myRules,
    };
  },
});
</script>
