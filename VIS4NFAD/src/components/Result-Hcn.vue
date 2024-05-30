<template>
  <el-table :data="tableData" style="width: 100%" height="150">
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
    <el-table-column label="smooth" width="200" >
      <template #default="scope">
        <el-progress :text-inside="true" :stroke-width="15" :percentage="scope.row.smooth*100" />
          </template>
    </el-table-column>
    <el-table-column label="operate">
      <template #default="scope">
        <el-button size="small">
          search
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script lang="ts" setup>
import { Timer } from '@element-plus/icons-vue'

interface User {
  date: string
  name: string
  address: string
}

const handleEdit = (index: number, row: User) => {
  console.log(index, row)
}
const handleDelete = (index: number, row: User) => {
  console.log(index, row)
}

const tableData: User[] = [
  {
    distance: 234,
    hcn: '4056/hcn_ne001',
    smooth: 0.88,
  },{
    distance: 234,
    hcn: '4056/hcn_ne001',
    smooth: 0.88,
  },{
    distance: 234,
    hcn: '4056/hcn_ne001',
    smooth: 0.88,
  },{
    distance: 234,
    hcn: '4056/hcn_ne001',
    smooth: 0.88,
  },{
    distance: 234,
    hcn: '4056/hcn_ne001',
    smooth: 0.88,
  }
]
</script>
