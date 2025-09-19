<template>
  <div class="osgb-panel">
    <h2>OSGB 转 3DTiles</h2>
    <form @submit.prevent="handleConvert">
      <div class="form-group">
        <label for="osgbPath">OSGB文件夹路径：</label>
        <div style="display: flex; gap: 8px">
          <input
            id="osgbPath"
            v-model="osgbPath"
            type="text"
            placeholder="请输入OSGB数据文件夹路径"
            style="flex: 1"
            readonly
          />
          <input
            type="file"
            webkitdirectory
            directory
            multiple
            @change="handleOsgbFolder"
            style="width: 120px"
          />
        </div>
      </div>
      <div class="form-group">
        <label for="outputPath">输出3DTiles路径：</label>
        <input
          id="outputPath"
          v-model="outputPath"
          type="text"
          placeholder="请输入输出文件夹路径"
        />
      </div>
      <div class="form-group">
        <label for="options">转换参数：</label>
        <input
          id="options"
          v-model="options"
          type="text"
          placeholder="可选参数（如坐标系等）"
        />
      </div>
      <button class="primary" type="submit" :disabled="isConverting">
        {{ isConverting ? "转换中..." : "开始转换" }}
      </button>
    </form>
    <div v-if="log" class="convert-log">
      <h3>转换日志</h3>
      <pre>{{ log }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const osgbPath = ref("");
const outputPath = ref("");
const options = ref("");
const isConverting = ref(false);
const log = ref("");

// 文件夹选择事件
const handleOsgbFolder = (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    // 获取文件夹路径（取第一个文件的路径的父目录）
    const firstFile = files[0];
    // @ts-ignore
    const fullPath = firstFile.webkitRelativePath || firstFile.name;
    // 只取文件夹名
    const folder = fullPath.split("/")[0];
    osgbPath.value = folder;
  }
};

const handleConvert = async () => {
  if (!osgbPath.value || !outputPath.value) {
    log.value = "请输入完整路径！";
    return;
  }
  isConverting.value = true;
  log.value = "正在转换，请稍候...\n";
  try {
    // 这里应调用后端API或本地命令行工具
    await new Promise((resolve) => setTimeout(resolve, 2000));
    log.value += "转换完成！\n输出路径：" + outputPath.value;
  } catch (e) {
    log.value += "转换失败：" + (e as Error).message;
  }
  isConverting.value = false;
};
</script>

<style scoped>
.osgb-panel {
  background: rgba(42, 42, 42, 0.95);
  color: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.18);
  max-width: 420px;
  margin: 40px auto;
}
.osgb-panel h2 {
  color: #3498db;
  margin-bottom: 18px;
}
.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}
label {
  margin-bottom: 6px;
  font-weight: 500;
}
input[type="text"] {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #34495e;
  background: #222;
  color: #fff;
  font-size: 15px;
}
input[type="file"] {
  background: #222;
  color: #fff;
  border-radius: 6px;
  border: 1px solid #34495e;
  font-size: 15px;
  padding: 6px 0;
}
button.primary {
  background: #3498db;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
  transition: background 0.2s;
}
button.primary:disabled {
  background: #888;
  cursor: not-allowed;
}
button.primary:hover:not(:disabled) {
  background: #217dbb;
}
.convert-log {
  margin-top: 24px;
  background: rgba(0, 0, 0, 0.12);
  border-radius: 6px;
  padding: 12px;
  color: #eee;
  font-size: 14px;
}
</style>
