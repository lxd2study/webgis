<template>
  <div>
    <!-- 左侧主工具栏 -->
    <div class="main-toolbar">
      <button
        @click="togglePanel('layers')"
        :class="{ active: activePanel === 'layers' }"
      >
        <span class="btn-icon">🗺️</span>
        图层功能
      </button>
      <button @click="togglePanel('data')" :class="{ active: activePanel === 'data' }">
        <span class="btn-icon">📊</span>
        数据解析
      </button>
    </div>

    <!-- 右侧功能面板 -->
    <div class="side-panel" :class="{ open: activePanel !== null }">
      <div class="panel-header">
        <h3>{{ panelTitle }}</h3>
        <button class="close-btn" @click="activePanel = null">
          <span class="close-icon">×</span>
        </button>
      </div>
      <div class="panel-content">
        <!-- 图层功能 -->
        <div v-if="activePanel === 'layers'">
          <div class="panel-group">
            <label>底图切换</label>
            <div class="select-wrapper">
              <select v-model="selectedImageryName" @change="changeImageryProvider">
                <option
                  v-for="provider in imageryProviders"
                  :key="provider.name"
                  :value="provider.name"
                >
                  {{ provider.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="panel-group">
            <label>视角操作</label>
            <div class="button-group">
              <button class="primary" @click="resetView">
                <span class="btn-icon">🎯</span>
                复位
              </button>
              <button @click="saveBookmark">
                <span class="btn-icon">📌</span>
                保存书签
              </button>
            </div>
            <div class="select-wrapper">
              <select v-model="selectedBookmarkIndex" @click="handleBookmarkClick">
                <option v-if="bookmarks.length === 0" disabled value="-1">
                  暂无书签
                </option>
                <option
                  v-for="(bookmark, index) in bookmarks"
                  :key="index"
                  :value="index"
                >
                  {{ bookmark.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="panel-group">
            <label>日照模拟</label>
            <div class="lighting-control">
              <input
                type="checkbox"
                id="lighting-toggle"
                v-model="enableLighting"
                @change="toggleLighting"
              />
              <label for="lighting-toggle" class="toggle-switch"></label>
              <input
                type="range"
                min="0"
                max="24"
                step="0.1"
                v-model="currentHour"
                @input="updateSunLight"
                :disabled="!enableLighting"
              />
              <span class="time-display"
                >{{ parseFloat(currentHour.toString()).toFixed(1) }} 时</span
              >
            </div>
          </div>
        </div>

        <!-- 数据解析功能 -->
        <div v-if="activePanel === 'data'">
          <div class="panel-group">
            <label>上传图片解析坐标</label>
            <label class="file-upload-btn">
              <span class="upload-icon">📤</span>
              <span>选择文件</span>
              <input type="file" @change="onImageChange" accept="image/*" />
            </label>
          </div>
          <div class="panel-group">
            <button
              class="danger"
              @click="clearAllPoints"
              :disabled="imageList.length === 0"
            >
              <span class="btn-icon">🗑️</span>
              清除所有地图标记点
            </button>
          </div>
          <div class="data-table-container">
            <table v-if="imageList.length > 0">
              <thead>
                <tr>
                  <th>名称</th>
                  <th>缩略图</th>
                  <th>坐标</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(img, idx) in imageList" :key="idx">
                  <td class="image-name">{{ img.name }}</td>
                  <td>
                    <div class="thumbnail-wrapper">
                      <img :src="img.url" alt="缩略图" class="thumbnail" />
                    </div>
                  </td>
                  <td>
                    <span v-if="img.latitude && img.longitude" class="coordinates">
                      {{ img.latitude.toFixed(4) }}, {{ img.longitude.toFixed(4) }}
                    </span>
                    <span v-else class="text-muted">
                      <span class="loading-spinner"></span>
                      解析中...
                    </span>
                  </td>
                  <td>
                    <button
                      class="action-btn"
                      @click="flyToImage(img)"
                      :disabled="!img.latitude || !img.longitude"
                    >
                      <span class="btn-icon">📍</span>
                      跳转
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="no-data">
              <span class="no-data-icon">📷</span>
              <span>暂无图片数据</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  --primary-color: #00aaff;
  --primary-gradient: linear-gradient(135deg, #00aaff 0%, #0099ee 100%);
  --dark-bg: rgba(25, 28, 34, 0.95);
  --panel-bg: rgba(33, 37, 43, 0.98);
  --control-bg: #2c313a;
  --control-hover-bg: #383e47;
  --text-color: #f8f9fa;
  --text-muted-color: #adb5bd;
  --border-color: #495057;
  --danger-color: #e74c3c;
  --danger-gradient: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
  --transition-base: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 左侧主工具栏 */
.main-toolbar {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: var(--dark-bg);
  padding: 12px;
  border-radius: 16px;
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.main-toolbar button {
  background: transparent;
  color: var(--text-color);
  border: 2px solid transparent;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: var(--transition-base);
  font-size: 15px;
  width: 140px;
  text-align: center;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.main-toolbar button:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.main-toolbar button.active {
  background: var(--primary-gradient);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(0, 170, 255, 0.4);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 18px;
  line-height: 1;
}

/* 右侧功能面板 */
.side-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 400px;
  height: 100%;
  background: var(--panel-bg);
  box-shadow: -10px 0 40px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  transform: translateX(100%);
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  color: var(--text-color);
  backdrop-filter: blur(12px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.side-panel.open {
  transform: translateX(0);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
  background: linear-gradient(to bottom, rgba(33, 37, 43, 0.98), rgba(33, 37, 43, 0.95));
}

.panel-header h3 {
  margin: 0;
  font-size: 22px;
  color: var(--primary-color);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.close-btn {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: var(--text-muted-color);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-base);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  transform: rotate(90deg);
}

.close-icon {
  line-height: 1;
}

.panel-content {
  padding: 25px;
  overflow-y: auto;
  flex-grow: 1;
}

/* 自定义滚动条 */
.panel-content::-webkit-scrollbar,
.data-table-container::-webkit-scrollbar {
  width: 8px;
}
.panel-content::-webkit-scrollbar-track,
.data-table-container::-webkit-scrollbar-track {
  background: transparent;
}
.panel-content::-webkit-scrollbar-thumb,
.data-table-container::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}
.panel-content::-webkit-scrollbar-thumb:hover,
.data-table-container::-webkit-scrollbar-thumb:hover {
  background: #666;
}

.panel-group {
  margin-bottom: 30px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-group label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
  color: #dee2e6;
  letter-spacing: 0.3px;
}

/* 通用控件样式 */
button {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--control-bg);
  color: var(--text-color);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: 15px;
  width: 100%;
  box-sizing: border-box;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

button:hover {
  background: var(--control-hover-bg);
  border-color: #5e6872;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

button.primary {
  background: var(--primary-gradient);
  border: none;
  color: #fff;
  font-weight: 600;
}
button.primary:hover {
  background: linear-gradient(135deg, #33bbff 0%, #2299ee 100%);
  box-shadow: 0 4px 12px rgba(0, 170, 255, 0.3);
}

button.danger {
  background: var(--danger-gradient);
  border: none;
  color: #fff;
  font-weight: 600;
}
button.danger:hover {
  background: linear-gradient(135deg, #ff6b5a 0%, #ee5a50 100%);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

button:disabled {
  background: #555;
  cursor: not-allowed;
  opacity: 0.6;
  border-color: #555;
  transform: none;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

/* 自定义 Select */
.select-wrapper {
  position: relative;
}
.select-wrapper::after {
  content: "▼";
  position: absolute;
  top: 50%;
  right: 15px;
  transform: translateY(-50%);
  font-size: 12px;
  color: var(--text-muted-color);
  pointer-events: none;
  transition: var(--transition-base);
}
select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--control-bg);
  color: var(--text-color);
  cursor: pointer;
  transition: var(--transition-base);
  font-size: 15px;
}
select:hover {
  background: var(--control-hover-bg);
  border-color: #5e6872;
}
select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 170, 255, 0.1);
}

/* 自定义文件上传按钮 */
.file-upload-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: 2px dashed var(--border-color);
  border-radius: 10px;
  background: var(--control-bg);
  color: var(--text-muted-color);
  cursor: pointer;
  transition: var(--transition-base);
  text-align: center;
}
.file-upload-btn:hover {
  background: var(--control-hover-bg);
  color: var(--text-color);
  border-color: var(--primary-color);
  transform: translateY(-1px);
}
.file-upload-btn input[type="file"] {
  display: none;
}

.upload-icon {
  font-size: 20px;
}

/* 日照模拟控件 */
.lighting-control {
  display: flex;
  align-items: center;
  gap: 15px;
  background: var(--control-bg);
  padding: 10px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
.lighting-control span.time-display {
  width: 60px;
  text-align: right;
  font-size: 14px;
  color: var(--text-muted-color);
  font-weight: 400;
}

/* 自定义 Checkbox (Toggle Switch) */
input[type="checkbox"] {
  display: none;
}
.toggle-switch {
  position: relative;
  top: 5px;
  display: inline-block;
  width: 48px;
  height: 26px;
  background-color: #494949;
  border-radius: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.toggle-switch::after {
  content: "";
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: rgb(255, 255, 255);
  top: 3px;
  left: 4px;
  transition: transform 0.3s;
  box-shadow: var(--shadow-sm);
}
input[type="checkbox"]:checked + .toggle-switch {
  background: var(--primary-gradient);
  background-color: #b8b8b8;
}
input[type="checkbox"]:checked + .toggle-switch::after {
  transform: translateX(18px);
}

/* 自定义 Range Slider */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 60%;
  height: 6px;
  background: #495057;
  border-radius: 3px;
  outline: none;
  flex-grow: 1;
}
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  transition: var(--transition-base);
  box-shadow: var(--shadow-md);
}
input[type="range"]::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: var(--shadow-md);
}
input[type="range"]:disabled::-webkit-slider-thumb {
  background: #888;
}
input[type="range"]:not(:disabled)::-webkit-slider-thumb:hover {
  background: #f0f0f0;
  transform: scale(1.1);
}
input[type="range"]:not(:disabled) {
  accent-color: var(--primary-color);
}

/* 数据解析表格 */
.data-table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}
th {
  background: #383e47;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: 0.5px;
}
tbody tr {
  transition: var(--transition-base);
}
tbody tr:last-child td {
  border-bottom: none;
}
tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}
td {
  vertical-align: middle;
  font-size: 14px;
}

.thumbnail-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: var(--transition-base);
}

.thumbnail:hover {
  transform: scale(1.05);
}

.image-name {
  font-weight: 500;
  color: var(--text-color);
}

.coordinates {
  font-family: "Courier New", monospace;
  color: var(--primary-color);
  font-weight: 500;
}

.action-btn {
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 8px;
}

.text-muted {
  color: var(--text-muted-color);
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--text-muted-color);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.no-data {
  text-align: center;
  padding: 40px;
  color: var(--text-muted-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.no-data-icon {
  font-size: 48px;
  opacity: 0.5;
}
</style>

<script setup lang="ts">
// 导入依赖
import { ref, onMounted, computed } from "vue";
import * as Cesium from "cesium";
import axios from "axios";

// --- 响应式状态 ---

// 面板控制
const activePanel = ref<"layers" | "data" | null>(null);

// 底图切换相关类型和变量
interface ImageryProviderItem {
  name: string;
  provider: Cesium.ImageryProvider;
}
const imageryProviders = ref<ImageryProviderItem[]>([]);
const selectedImageryName = ref<string>("");

// 书签相关类型和变量
interface Bookmark {
  name: string;
  position: Cesium.Cartesian3;
  orientation: {
    heading: number;
    pitch: number;
    roll: number;
  };
}
const bookmarks = ref<Bookmark[]>([]);
const selectedBookmarkIndex = ref<number>(-1);

// 日照模拟相关变量
const enableLighting = ref(false);
const currentHour = ref(12);

// 图片列表类型
interface ImageItem {
  name: string;
  url: string;
  latitude?: number;
  longitude?: number;
}
const imageList = ref<ImageItem[]>([]);

// 图片解析接口返回类型
interface ParseImageResponse {
  latitude?: number;
  longitude?: number;
  error?: string;
}

// --- 计算属性 ---

const panelTitle = computed(() => {
  if (activePanel.value === "layers") return "图层功能";
  if (activePanel.value === "data") return "数据解析";
  return "";
});

// --- 方法 ---

// 获取 Cesium Viewer 实例
const getViewer = (): Cesium.Viewer | undefined => (window as any).viewer;

// 切换面板
const togglePanel = (panel: "layers" | "data") => {
  if (activePanel.value === panel) {
    activePanel.value = null;
  } else {
    activePanel.value = panel;
  }
};

// 初始化底图列表
const initImageryProviders = () => {
  imageryProviders.value = [
    {
      name: "天地图影像",
      provider: new Cesium.WebMapTileServiceImageryProvider({
        url:
          "https://t0.tianditu.gov.cn/img_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=img&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd",
        layer: "tdtImgLayer",
        style: "default",
        format: "image/jpeg",
        tileMatrixSetID: "GoogleMapsCompatible",
        maximumLevel: 18,
      }),
    },
    {
      name: "天地图路网",
      provider: new Cesium.WebMapTileServiceImageryProvider({
        url:
          "https://t0.tianditu.gov.cn/cia_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=cia&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd",
        layer: "tdtAnnoLayer",
        style: "default",
        format: "image/jpeg",
        tileMatrixSetID: "GoogleMapsCompatible",
        maximumLevel: 18,
      }),
    },
  ];
  selectedImageryName.value = imageryProviders.value[0].name;
};

// 切换底图
const changeImageryProvider = () => {
  const viewer = getViewer();
  const providerItem = imageryProviders.value.find(
    (p) => p.name === selectedImageryName.value
  );
  if (viewer && providerItem) {
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(providerItem.provider);
  }
};

// 复位视角
const resetView = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.camera.flyTo({
      destination: new Cesium.Cartesian3(
        -7528076.842831879,
        22246599.852625612,
        15848492.331951736
      ),
      orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_TWO, roll: 0 },
    });
  }
};

// 保存当前视角为书签
const saveBookmark = () => {
  const viewer = getViewer();
  if (viewer) {
    const camera = viewer.camera;
    const name = window.prompt("请输入书签名称", `书签 ${bookmarks.value.length + 1}`);
    if (name && name.trim()) {
      bookmarks.value.push({
        name: name.trim(),
        position: camera.position.clone(),
        orientation: {
          heading: camera.heading,
          pitch: camera.pitch,
          roll: camera.roll,
        },
      });
      selectedBookmarkIndex.value = bookmarks.value.length - 1;
    }
  }
};

// 处理书签点击事件
const handleBookmarkClick = () => {
  // 如果已经选中了一个书签，则直接跳转
  if (selectedBookmarkIndex.value >= 0) {
    flyToBookmark();
  }
};

// 修改原来的 flyToBookmark 方法
const flyToBookmark = () => {
  const viewer = getViewer();
  const bookmark = bookmarks.value[selectedBookmarkIndex.value];
  if (viewer && bookmark && selectedBookmarkIndex.value >= 0) {
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.clone(bookmark.position),
      orientation: bookmark.orientation,
    });
  }
};


// 切换日照模拟
const toggleLighting = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.scene.globe.enableLighting = enableLighting.value;
    if (enableLighting.value) {
      updateSunLight();
    }
  }
};

// 更新太阳光照时间
const updateSunLight = () => {
  const viewer = getViewer();
  if (viewer && enableLighting.value) {
    const now = new Date();
    const date = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      Number(currentHour.value),
      (Number(currentHour.value) * 60) % 60,
      0
    );
    viewer.clock.currentTime = Cesium.JulianDate.fromDate(date);
  }
};

// 处理图片选择事件
const onImageChange = (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    const file = files[0];
    const url = URL.createObjectURL(file);
    uploadAndParseImage(file, url);
    (e.target as HTMLInputElement).value = "";
  }
};

// 上传图片并解析坐标
const uploadAndParseImage = async (file: File, url: string) => {
  const formData = new FormData();
  formData.append("image", file);

  const newImage: ImageItem = { name: file.name, url };
  imageList.value.push(newImage);

  try {
    const res = await axios.post<ParseImageResponse>(
      "http://localhost:5000/parse_image",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    if (res.data.latitude && res.data.longitude) {
      // 使用响应式更新
      const index = imageList.value.findIndex((img) => img.url === url);
      if (index !== -1) {
        imageList.value[index] = {
          ...imageList.value[index],
          latitude: res.data.latitude,
          longitude: res.data.longitude,
        };
      }
      flyToImage(imageList.value[index]); // 解析成功后自动跳转
    } else {
      throw new Error(res.data.error || "解析返回数据无效");
    }
  } catch (err) {
    console.error("图片解析失败:", err);
    alert(`图片 "${file.name}" 解析失败`);
    const index = imageList.value.findIndex((img) => img.url === url);
    if (index !== -1) {
      imageList.value[index] = {
        ...imageList.value[index],
        latitude: undefined,
        longitude: undefined,
      };
    }
  }
};

// 跳转到图片坐标并在地图上标记
const flyToImage = (img: ImageItem) => {
  if (!img.latitude || !img.longitude) return;
  const viewer = getViewer();
  if (viewer) {
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(img.longitude, img.latitude, 2000),
    });
    viewer.entities.add({
      position: Cesium.Cartesian3.fromDegrees(img.longitude, img.latitude, 10),
      point: {
        pixelSize: 12,
        color: Cesium.Color.fromCssColorString("var(--primary-color)"),
      },
      label: {
        text: `${img.name}\n${img.latitude.toFixed(6)}, ${img.longitude.toFixed(6)}`,
        font: "16px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -20),
      },
    });
  }
};

// 清除所有由图片解析添加的点
const clearAllPoints = () => {
  const viewer = getViewer();
  if (viewer) {
    const entitiesToRemove = viewer.entities.values.filter(
      (entity) => entity.label && entity.point
    );
    entitiesToRemove.forEach((entity) => viewer.entities.remove(entity));
    imageList.value = [];
  }
};

// --- 生命周期钩子 ---

onMounted(initImageryProviders);
</script>
