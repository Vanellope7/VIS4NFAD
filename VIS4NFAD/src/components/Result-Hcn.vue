<template>
  <el-table :data="combinedTableData" style="width: 100%" height="320">
    <el-table-column label="Distance">
      <template #default="scope">
        <div style="display: flex; align-items: center">
          <el-tag>{{ scope.row.distance }}</el-tag>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="Hcn">
      <template #default="scope">
        {{ scope.row.hcn }}
      </template>
    </el-table-column>
    <el-table-column label="Smooth" width="200">
      <template #default="scope">
        <el-progress :text-inside="true" :stroke-width="15" :percentage="parseFloat((scope.row.smooth * 100.0).toFixed(2))" />
      </template>
    </el-table-column>
    <el-table-column label="Operate" header-align="right" align="right">
      <template #default="scope">
        <el-button size="small" type="primary" @click="handleSearch(scope.$index, scope.row)">
          Search
        </el-button>
        <el-button size="small" type="success" @click="handleSave(scope.$index, scope.row)">
          Save
        </el-button>
        <el-button size="small" type="danger" @click="handleDelete(scope.$index, scope.row)">
          Delete
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const tableData = ref([]);
const savedData = ref([]);

const combinedTableData = computed(() => {
  return [...tableData.value, ...savedData.value];
});

const fetchData = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/get_table_data');
    tableData.value = response.data;
  } catch (error) {
    console.error('Error fetching table data:', error);
  }
};

const handleSave = (index, row) => {
  if (!savedData.value.includes(row)) {
    savedData.value.push({ ...row });
  }
};

const handleDelete = (index, row) => {
  if (tableData.value.includes(row)) {
    tableData.value.splice(index, 1);
  } else if (savedData.value.includes(row)) {
    savedData.value.splice(index, 1);
  }
};

const handleSearch = (index, row) => {
  console.log('Search clicked:', index, row);
};

// Fetch data when the component is mounted
onMounted(() => {
  fetchData();
});
</script>
