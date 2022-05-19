<template>
  <canvas class="q-pa-xl" id="chart" ref="chart"></canvas>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';
import { useQuasar } from 'quasar';
import { ChartData } from 'chart.js';
import Chart from 'chart.js/auto';
import { AccountService } from '..';
import { ProviderService } from '..';
import { Account } from '../models/Account';
import { Iaas } from '../models/Iaas';
import { MetricService } from '../services/MetricService';

function onlyUnique(value: any, index: any, self: any) {
  return self.indexOf(value) === index;
}

const colors = ['#ff0000', '#0000ff'];

export default defineComponent({
  name: 'MetricPage',

  setup() {
    const $q = useQuasar();
    const data: ChartData = {
      labels: [],
      datasets: [],
    } as ChartData;
    var chart: Chart;

    async function update() {
      var count = 0;
      MetricService.getAllMetrics().then((resp) => {
        resp = resp.map((m: any) => {
          for (var i = 0; i < m.data.length; i++) {
            if (data.labels!.includes(m.data[i].x)) {
              continue;
            }
            data.labels!.push(m.data[i].x);
          }
          m.fill = false;
          m.borderColor = colors[count++];
          m.tension = 0.1;
          return m;
        });

        data.datasets.push(...resp);
        chart.data = data;
        chart.update();
      });
    }

    onUnmounted(() => {
      if (chart) {
        chart.destroy();
      }
    });

    onMounted(async () => {
      const ctx = (
        document.getElementById('chart') as HTMLCanvasElement
      ).getContext('2d');
      if (!ctx) {
        console.error('Failed to get context');
        return;
      }
      chart = new Chart(ctx, {
        type: 'line',
        data: {} as ChartData,
        options: {},
      });
    });
    update();
  },
});
</script>
