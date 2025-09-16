<template>
  <div class="toolbar">
    <div class="toolbar-group">
      <div class="toolbar-item">
        <label>底图：</label>
        <select v-model="selectedImageryName" @change="changeImageryProvider">
          <option v-for="provider in imageryProviders" :key="provider.name" :value="provider.name">
            {{ provider.name }}
          </option>
        </select>
      </div>
    </div>
    <div class="toolbar-divider"></div>
    <div class="toolbar-group">
      <div class="toolbar-item">
        <button class="primary" @click="resetView">复位</button>
      </div>
    </div>
    <div class="toolbar-divider"></div>
    <div class="toolbar-group">
      <div class="toolbar-item">
        <button @click="saveBookmark">保存书签</button>
        <select v-model="selectedBookmarkIndex" @change="flyToBookmark" class="bookmark-select">
          <option v-for="(bookmark, index) in bookmarks" :key="index" :value="index">
            {{ bookmark.name }}
          </option>
        </select>
      </div>
    </div>
    <div class="toolbar-divider"></div>
    <div class="toolbar-group">
      <div class="toolbar-item">
        <label>日照模拟：</label>
        <input type="checkbox" v-model="enableLighting" @change="toggleLighting" />
        <input type="range" min="0" max="24" step="0.1" v-model="currentHour" @input="updateSunLight" />
        <span>{{ currentHour }} 时</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: rgba(42, 42, 42, 0.85);
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.2);
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
  backdrop-filter: blur(4px);
  min-width: 320px;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-divider {
  width: 2px;
  height: 32px;
  background: rgba(255,255,255,0.08);
  border-radius: 2px;
  margin: 0 8px;
}

.toolbar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

button,
select {
  padding: 6px 14px;
  border: none;
  border-radius: 5px;
  background: #2c3e50;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 15px;
}

button.primary {
  background: #3498db;
}

button:hover,
select:hover {
  background: #34495e;
}

.bookmark-select {
  min-width: 120px;
  max-width: 180px;
}

label {
  font-size: 15px;
  font-weight: 500;
}

input[type="range"] {
  accent-color: #3498db;
  width: 100px;
}
</style>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import * as Cesium from "cesium";

interface ImageryProviderItem {
  name: string;
  provider: Cesium.ImageryProvider;
}

interface Bookmark {
  name: string;
  position: Cesium.Cartesian3;
  orientation: {
    heading: number;
    pitch: number;
    roll: number;
  };
}

const imageryProviders = ref<ImageryProviderItem[]>([]);
const selectedImageryName = ref<string>("");
const bookmarks = ref<Bookmark[]>([]);
const selectedBookmarkIndex = ref<number>(-1);
const enableLighting = ref(false);
const currentHour = ref(12);

const getViewer = (): Cesium.Viewer | undefined => (window as any).viewer;

const initImageryProviders = () => {
  imageryProviders.value = [
    {
      name: "天地图",
      provider: new Cesium.WebMapTileServiceImageryProvider({
        url: "https://t0.tianditu.gov.cn/img_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=img&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd",
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
        url: "https://t0.tianditu.gov.cn/cia_w/wmts?service=wmts&request=GetTile&version=1.0.0&LAYER=cia&tileMatrixSet=w&TileMatrix={TileMatrix}&TileRow={TileRow}&TileCol={TileCol}&style=default&format=tiles&tk=ac919d63816e20e2179ef656191edacd",
        layer: "tdtAnnoLayer",
        style: "default",
        format: "image/jpeg",
        tileMatrixSetID: "GoogleMapsCompatible",
        maximumLevel: 18,
      }),
    },
  ];
  selectedImageryName.value = imageryProviders.value[1].name;
};

const changeImageryProvider = () => {
  const viewer = getViewer();
  const provider = imageryProviders.value.find(p => p.name === selectedImageryName.value)?.provider;
  if (viewer && provider) {
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(provider);
  }
};

const resetView = () => {
  const viewer = getViewer();
  // 如果有选中的书签，则飞到书签位置
  if (
    viewer &&
    selectedBookmarkIndex.value >= 0 &&
    bookmarks.value[selectedBookmarkIndex.value]
  ) {
    const bookmark = bookmarks.value[selectedBookmarkIndex.value];
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.clone(bookmark.position),
      orientation: bookmark.orientation,
    });
  } else if (viewer) {
    // 否则回到默认视角
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(116.39, 39.9, 10000),
      orientation: { heading: 0, pitch: -Cesium.Math.PI_OVER_TWO, roll: 0 },
    });
  }
};

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
    }
  }
};

const flyToBookmark = () => {
  const viewer = getViewer();
  const bookmark = bookmarks.value[selectedBookmarkIndex.value];
  if (viewer && bookmark) {
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.clone(bookmark.position),
      orientation: bookmark.orientation,
    });
  }
};

const toggleLighting = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.scene.globe.enableLighting = enableLighting.value;
  }
};

const updateSunLight = () => {
  const viewer = getViewer();
  if (viewer) {
    const now = new Date();
    const date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), currentHour.value, 0, 0);
    viewer.clock.currentTime = Cesium.JulianDate.fromDate(date);
  }
};

onMounted(initImageryProviders);
</script>
