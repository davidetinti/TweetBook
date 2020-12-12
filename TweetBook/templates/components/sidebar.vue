<template>
  <!-- Left Sidebar -->
  <div
    id="sidebar"
    class="d-flex flex-column align-items-center justify-content-between pt-2"
  >
    <!-- Sections Buttons -->
    <div class="d-flex flex-column align-items-center">
      <button
        v-for="(section, index) in sections"
        @click="$emit('changed-section', index)"
        :key="index"
        class="sidebar-button my-2"
        :id="`popover-${section.name}`"
      >
        <em class="fas" :class="section.icon"></em>
        <b-popover
          :target="`popover-${section.name}`"
          triggers="hover"
          placement="right"
          :content="`${section.popover_name}`"
          :delay="{ show: 700, hide: 50 }"
        ></b-popover>
      </button>
    </div>
    <!-- Settings and Logo -->
    <div class="d-flex flex-column align-items-center">
      <button
        @click="$emit('changed-section', -1)"
        class="sidebar-button my-2"
        id="popover-settings"
      >
        <em class="fas fa-cog"></em>
        <b-popover
          target="popover-settings"
          triggers="hover"
          placement="right"
          content="Impostazioni"
          :delay="{ show: 700, hide: 50 }"
        ></b-popover>
      </button>
      {% load static %}
      <!-- Load from static path ../static/images -->
      <img
        class="sidebar-icon my-2"
        src="{% static 'images/logo.png' %}"
        alt="TweetBook Logo"
      />
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {};
  },
  props: {
    active_section: Object,
    sections: Array,
  },
};
</script>

<style>
#sidebar {
  height: 100%;
  width: var(--sidebar-width);
  background-color: rgb(26, 40, 55);
  border-right: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

#sidebar .sidebar-button {
  transition: 0.5s;
  height: 50px;
  width: 50px;
  background-color: transparent;
  border: rgb(22, 159, 242) solid 1px;
  box-sizing: border-box;
  border-radius: 50%;
  outline: none;
}

#sidebar .sidebar-button * {
  color: rgb(22, 159, 242);
}

#sidebar .sidebar-button:hover {
  transition: 0.5s;
  cursor: pointer;
  background-color: #d9dcd6;
  border: #0a1128 solid 1px;
}

#sidebar .sidebar-button:hover * {
  transition: 0.5s;
  color: #0a1128;
}

#sidebar .sidebar-button.active {
  border: #ffffff solid 1px;
}

#sidebar .sidebar-button.active * {
  color: #ffffff;
}

#sidebar .sidebar-icon {
  height: 50px;
  width: 50px;
  box-sizing: border-box;
}
</style>
