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
