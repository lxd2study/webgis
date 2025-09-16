<template>
  <div class="toolbar">
    <div class="toolbar-group">
      <div class="toolbar-item">
        <label>底图：</label>
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
        <select
          v-model="selectedBookmarkIndex"
          @change="flyToBookmark"
          class="bookmark-select"
        >
          <option v-if="bookmarks.length === 0" disabled value="-1">暂无书签</option>
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
    <div class="toolbar-divider"></div>
    <div class="toolbar-group">
      <div class="toolbar-item">
        <label>图片坐标解析：</label>
        <input type="file" @change="onImageChange" accept="image/*" />
        <button @click="parseImage" :disabled="!selectedImage">解析图片</button>
        <span v-if="imageCoords"
          >坐标: {{ imageCoords.latitude }}, {{ imageCoords.longitude }}</span
        >
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
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
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
  background: rgba(255, 255, 255, 0.08);
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
// 导入依赖
import { ref, onMounted } from "vue";
import * as Cesium from "cesium";
import axios from "axios";

// 底图切换相关类型和变量
interface ImageryProviderItem {
  name: string;
  provider: Cesium.ImageryProvider;
}

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

// 底图列表
const imageryProviders = ref<ImageryProviderItem[]>([]);
// 当前选中的底图名称
const selectedImageryName = ref<string>("");

// 书签列表
const bookmarks = ref<Bookmark[]>([]);
// 当前选中的书签索引
const selectedBookmarkIndex = ref<number>(-1);

// 日照模拟相关变量
const enableLighting = ref(false);
const currentHour = ref(12);

// 图片解析接口返回类型
interface ParseImageResponse {
  latitude?: number;
  longitude?: number;
  error?: string;
}

// 获取 Cesium Viewer 实例
const getViewer = (): Cesium.Viewer | undefined => (window as any).viewer;

// 初始化底图列表
const initImageryProviders = () => {
  imageryProviders.value = [
    {
      name: "天地图",
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
  selectedImageryName.value = imageryProviders.value[1].name;
};

// 切换底图
const changeImageryProvider = () => {
  const viewer = getViewer();
  const provider = imageryProviders.value.find(
    (p) => p.name === selectedImageryName.value
  )?.provider;
  if (viewer && provider) {
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(provider);
  }
};

// 复位视角
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
    }
  }
};

// 飞到选中的书签
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

// 切换日照模拟
const toggleLighting = () => {
  const viewer = getViewer();
  if (viewer) {
    viewer.scene.globe.enableLighting = enableLighting.value;
  }
};

// 更新太阳光照时间
const updateSunLight = () => {
  const viewer = getViewer();
  if (viewer) {
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

// 图片上传相关变量
const selectedImage = ref<File | null>(null);
// 图片解析结果（坐标）
const imageCoords = ref<{ latitude: number; longitude: number } | null>(null);

// 处理图片选择事件
const onImageChange = (e: Event) => {
  const files = (e.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    selectedImage.value = files[0];
  } else {
    selectedImage.value = null;
  }
};

// 解析图片，获取坐标并显示在地图上
const parseImage = async () => {
  if (!selectedImage.value) return;
  const formData = new FormData();
  formData.append("image", selectedImage.value);

  try {
    const res = await axios.post<ParseImageResponse>("http://localhost:5000/parse_image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    if (res.data.latitude && res.data.longitude) {
      imageCoords.value = {
        latitude: res.data.latitude,
        longitude: res.data.longitude,
      };
      showImageCoordOnMap(res.data.latitude, res.data.longitude);
    } else {
      imageCoords.value = null;
      alert(res.data.error || "解析失败");
    }
  } catch (err) {
    alert("图片解析失败");
  }
};

// 在地图上显示图片解析得到的坐标点
const showImageCoordOnMap = (lat: number, lng: number) => {
  const viewer = getViewer();
  if (viewer) {
    // 清除之前的图片点（通过id或全部清除）
    const entities = viewer.entities.values;
    for (let i = entities.length - 1; i >= 0; i--) {
      if (entities[i].id === "image-coord-point") {
        viewer.entities.remove(entities[i]);
      }
    }
    // 添加新点
    viewer.entities.add({
      id: "image-coord-point",
      position: Cesium.Cartesian3.fromDegrees(lng, lat, 10), // Cesium: lng, lat, height
      point: { pixelSize: 12, color: Cesium.Color.RED },
      label: {
        text: `图片坐标\n${lat.toFixed(6)}, ${lng.toFixed(6)}`,
        font: "16px sans-serif",
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -20),
      },
    });
    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(lng, lat, 2000),
    });
  }
};

// 页面加载时初始化底图
onMounted(initImageryProviders);
</script>
