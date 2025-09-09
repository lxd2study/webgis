<template>
  <div class="toolbar">
    <!-- 底图切换 -->
    <div class="toolbar-item">
      <label>底图：</label>
      <select v-model="selectedImageryProvider" @change="changeImageryProvider">
        <option
          v-for="provider in imageryProviders"
          :key="provider.name"
          :value="provider"
        >
          {{ provider.name }}
        </option>
      </select>
    </div>

    <!-- 复位按钮 -->
    <div class="toolbar-item">
      <button @click="resetView">复位</button>
    </div>

    <!-- 视角书签 -->
    <div class="toolbar-item">
      <button @click="saveBookmark">保存书签</button>
      <select v-model="selectedBookmark" @change="flyToBookmark">
        <option v-for="(bookmark, index) in bookmarks" :key="index" :value="bookmark">
          {{ bookmark.name }}
        </option>
      </select>
    </div>

    <!-- 日照模拟 -->
    <div class="toolbar-item">
      <label>日照模拟：</label>
      <input type="checkbox" v-model="enableLighting" @change="toggleLighting" />
      <input
        type="range"
        min="0"
        max="24"
        step="0.1"
        v-model="currentHour"
        @input="updateSunLight"
      />
      <span>{{ currentHour }} 时</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import * as Cesium from "cesium";

// 定义底图提供者的类型
interface ImageryProvider {
  name: string;
  provider: Cesium.ImageryProvider;
}

// 定义书签的类型
interface Bookmark {
  name: string;
  position: Cesium.Cartesian3;
  orientation: {
    heading: number;
    pitch: number;
    roll: number;
  };
}

// 当前选中的底图
const selectedImageryProvider = ref<ImageryProvider>();
// 底图列表
const imageryProviders = ref<ImageryProvider[]>([]);
// 书签列表
const bookmarks = ref<Bookmark[]>([]);
// 当前选中的书签
const selectedBookmark = ref<Bookmark>();
// 是否启用光照
const enableLighting = ref(false);
// 当前时间（小时）
const currentHour = ref(12);

// 获取Cesium Viewer实例
const getViewer = (): Cesium.Viewer | undefined => {
  // 通过全局方式获取，或者通过prop传入。这里假设我们通过window.viewer获取，但这不是最佳实践。
  return (window as any).viewer;
};

// 初始化底图列表
const initImageryProviders = () => {
  imageryProviders.value = [
    {
      name: "天地图",
      provider: new Cesium.WebMapTileServiceImageryProvider({
        // 服务URL地址，使用天地图提供的WMTS服务
        url: `https://t0.tianditu.gov.cn/img_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=img&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd`,
        // 图层名称
        layer: "tdtImgLayer",
        // 图层样式
        style: "default",
        // 图片格式
        format: "image/jpeg",
        // 瓦片矩阵集ID，使用Google Maps兼容的坐标系
        tileMatrixSetID: "GoogleMapsCompatible",
        // 最大缩放级别
        maximumLevel: 18,
      }),
    },
    {
      name: "天地图路网",
      provider: new Cesium.WebMapTileServiceImageryProvider({
        url: `https://t0.tianditu.gov.cn/cia_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=cia&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd`,
        layer: "tdtAnnoLayer",
        style: "default",
        format: "image/jpeg",
        tileMatrixSetID: "GoogleMapsCompatible",
        maximumLevel: 18,
      }),
    },
  ];
  selectedImageryProvider.value = imageryProviders.value[1];
};

// 切换底图
const changeImageryProvider = () => {
  const viewer = getViewer();
  if (viewer && selectedImageryProvider.value) {
    // 先移除现有的底图图层
    viewer.imageryLayers.removeAll();
    // 添加新的底图
    viewer.imageryLayers.addImageryProvider(selectedImageryProvider.value.provider);
  }
};

// 复位视角
const resetView = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(116.39, 39.9, 10000),
      orientation: {
        heading: 0,
        pitch: -Cesium.Math.PI_OVER_TWO,
        roll: 0,
      },
    });
  }
};

// 保存当前视角为书签
const saveBookmark = () => {
  const viewer = getViewer();
  if (viewer) {
    const camera = viewer.camera;
    const position = camera.position; // 世界坐标（米）
    const heading = camera.heading;
    const pitch = camera.pitch;
    const roll = camera.roll;

    const bookmark: Bookmark = {
      name: `书签 ${bookmarks.value.length + 1}`,
      position: position,
      orientation: {
        heading: heading,
        pitch: pitch,
        roll: roll,
      },
    };

    bookmarks.value.push(bookmark);
  }
};

// 飞到书签保存的视角
const flyToBookmark = () => {
  const viewer = getViewer();
  if (viewer && selectedBookmark.value) {
    const wz = Cesium.Cartesian3.fromElements(
      selectedBookmark.value.position.x,
      selectedBookmark.value.position.y,
      selectedBookmark.value.position.z
    );

    viewer.camera.flyTo({
      destination: wz,
      orientation: selectedBookmark.value.orientation,
    });
  }
};

// 切换日照模拟
const toggleLighting = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.scene.globe.enableLighting = enableLighting.value;
  }
};

// 更新太阳光位置（根据时间）
const updateSunLight = () => {
  const viewer = getViewer();
  if (viewer) {
    // 将当前时间设置为今天的一个特定小时
    const now = new Date();
    const date = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      currentHour.value,
      0,
      0
    );
    viewer.clock.currentTime = Cesium.JulianDate.fromDate(date);
  }
};

onMounted(() => {
  initImageryProviders();
});
</script>

<style scoped>
.toolbar {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: rgba(42, 42, 42, 0.8);
  padding: 10px;
  border-radius: 5px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.toolbar-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: white;
}

button,
select {
  padding: 5px 10px;
  border: none;
  border-radius: 3px;
  background: #2c3e50;
  color: white;
  cursor: pointer;
}

button:hover,
select:hover {
  background: #34495e;
}

label {
  font-size: 14px;
}
</style>
