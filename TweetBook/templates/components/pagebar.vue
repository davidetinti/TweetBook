<template>
  <!-- Bottom pages-bar -->
  <div class="pages-wrapper d-flex align-items-center">
    <b-button
      v-for="(page, index) in pages"
      @click="$emit('changed-page', index)"
      :key="index"
      class="page-button mx-2"
      :class="{ active: page == active_page }"
    >
      <div v-if="!page.name">Nuova ricerca</div>
      <div v-else>${ page.name }</div>
      <b-button
        @click="$emit('removed-page', index)"
        class="delete-page-button ml-4 p-0"
      >
        <em class="fas fa-times"></em>
      </b-button>
    </b-button>
    <b-button @click="$emit('added-page')" class="add-page-button mx-2">
      <em class="fas fa-plus"></em>
    </b-button>
  </div>
</template>

<script>
module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {};
  },
  props: {
    pages: Array,
    active_page: Object,
  },
  mounted: function () {
    // Rende la bottom page-bar scrollabile
    let ele = document.getElementsByClassName("pages-wrapper")[0];
    ele.style.cursor = "grab";

    let pos = {
      top: 0,
      left: 0,
      x: 0,
      y: 0,
    };

    let mouseDownHandler = function (e) {
      ele.style.cursor = "grabbing";
      ele.style.userSelect = "none";

      pos = {
        left: ele.scrollLeft,
        top: ele.scrollTop,
        // Get the current mouse position
        x: e.clientX,
        y: e.clientY,
      };

      document.addEventListener("mousemove", mouseMoveHandler);
      document.addEventListener("mouseup", mouseUpHandler);
    };

    let mouseMoveHandler = function (e) {
      // How far the mouse has been moved
      let dx = e.clientX - pos.x;
      let dy = e.clientY - pos.y;

      // Scroll the element
      ele.scrollTop = pos.top - dy;
      ele.scrollLeft = pos.left - dx;
    };

    let mouseUpHandler = function () {
      ele.style.cursor = "grab";
      ele.style.removeProperty("user-select");

      document.removeEventListener("mousemove", mouseMoveHandler);
      document.removeEventListener("mouseup", mouseUpHandler);
    };

    // Attach the handler
    ele.addEventListener("mousedown", mouseDownHandler);
  },
};
</script>

<style>
.pages-wrapper {
  height: var(--pagesbar-height);
  width: calc(100vw - var(--sidebar-width));
  font-size: 20px;
  overflow-x: scroll;
  border-top: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
  white-space: nowrap;
}

.pages-wrapper::-webkit-scrollbar {
  display: none;
}

.pages-wrapper .page-button {
  background-color: rgb(53, 64, 72);
  height: 65%;
  width: max-content;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0px;
  border-radius: 20px;
}

.pages-wrapper .page-button.active {
  background-color: white;
}

.delete-page-button {
  background-color: transparent;
  height: 100%;
  width: max-content;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0px;
  border-radius: 0px;
}

.add-page-button {
  background-color: rgb(53, 64, 72);
  height: 65%;
  width: max-content;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0px;
  border-radius: 20px;
}
</style>
