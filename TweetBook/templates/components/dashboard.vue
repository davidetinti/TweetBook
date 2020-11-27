<template>
  <div id="dashboard">
    <!-- Sidebar -->
    <sidebar
      :sections="sections"
      :active_section="active_section"
      @changed-section="setActiveSection"
    ></sidebar>

    <!-- Content on the right -->
    <div id="right-content" class="d-flex flex-column">
      <!-- Section content -->
      <div id="section-content">
        <search-section
          v-show="active_section == sections[0]"
          :page="active_page"
          @params-update="onParamsUpdate"
          @load-search="onLoadSearch"
          @recent-search-done="onRecentSearchDone"
        ></search-section>
        <map-section
          v-show="active_section == sections[1]"
          :page="active_page"
        ></map-section>
        <graph-section
          v-show="active_section == sections[2]"
          :page="active_page"
        ></graph-section>
      </div>
      <!-- Bottom pages-bar -->
      <pagebar
        :pages="pages"
        :active_page="active_page"
        @changed-page="setActivePage"
        @added-page="addPage"
        @removed-page="removePage"
      ></pagebar>
    </div>
  </div>
</template>

<script>
class MapParameters {
  constructor() {
    this.lat = 44.456348;
    this.lng = 11.574575;
    this.zoom = 4;
    this.poi = [];
    this.heat_markers = [];
  }
}

class SearchParameters {
  constructor() {
    this.keywords = "";
    this.retweets = false;
    this.replies = false;
    this.stream = false;
    this.user = "";
    this.location = "";
    this.hashtag = "";
    this.tag = "";
  }
}

class Section {
  constructor(name, popover_name, icon) {
    this.name = name;
    this.popover_name = popover_name;
    this.icon = icon;
  }
}

class Page {
  constructor() {
    this.id = Date.now();
    this.name = "";
    this.active_section = 0;
    this.search_parameters = new SearchParameters();
    this.maps = new MapParameters();
    this.tweets = [];
    this.selected_tweets = [];
    this.selected_geo_tweets = [];
    this.graphs = {};
  }
}

module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {
      sections: [
        new Section("searchSection", "Cerca", "fa-search"),
        new Section("mapSection", "Mappa", "fa-map-marker-alt"),
        new Section("graphSection", "Grafici", "fa-chart-bar"),
      ],
      active_page: null,
      pages: [new Page()],
    };
  },
  computed: {
    active_section: function () {
      return this.sections[this.active_page.active_section];
    },
  },
  methods: {
    setActiveSection(index) {
      if (index >= 0 && index < this.sections.length) {
        this.active_page.active_section = index;
      }
    },
    // può essere chiamata sia con l'oggetto che con l'indice
    setActivePage(val) {
      if (this.active_page) this.removeMarkers(this.active_page, null);
      switch (typeof val) {
        case "number":
          if (val >= 0 && val < this.pages.length) {
            this.active_page = this.pages[val];
          }
          break;
        case "object":
          this.active_page = val;
        default:
          break;
      }
    },
    addPage(page) {
      if (this.active_page) this.removeMarkers(this.active_page, null);
      this.pages.push(page ? page : new Page());
      this.active_page = this.pages[this.pages.length - 1];
    },
    removePage(index) {
      if (this.pages.length > 1) {
        this.removeMarkers(this.pages[index], null);
        this.pages.splice(index, 1);
        if (index == this.pages.indexOf(this.active_page)) {
          if (index == this.pages.length) this.setActivePage(index - 1);
          else this.setActivePage(index);
        }
      }
    },
    onParamsUpdate(new_value) {
      this.active_page.search_parameters = new_value;
    },
    onLoadSearch(page) {
      this.addPage(page);
      this.setActivePage(page);
      //se non è ancora stata fatta una ricerca nella
      //pagina corrente, la sostituisco con la caricata
      if (this.pages[0].tweets.length == 0) this.removePage(0);
    },
    onRecentSearchDone(page) {
      page.id = Date.now();
      page.maps.poi.forEach((poi) => {
        this.removeMarkers(null, poi);
      });
      page.maps = new MapParameters();
      page.selected_tweets = [];
      page.selected_geo_tweets = [];
      page.graphs = {};
    },
    removeMarkers(page, element) {
      //Primo caso: nascondo tutti i marker di quella pagina.
      if (page != null && element == null) {
        for (let poi of page.maps.poi) {
          poi.infowindow.close();
          poi.marker.setMap(null);
        }
      }
      //Secondo caso: rimuovo completamente un marker
      else if (page == null && element != null) {
        let indice = -1;
        for (let i = 0; i < this.page.maps.poi.length; i++) {
          if (
            element.infowindow.content ===
            this.active_page.maps.poi[i].infowindow.content
          )
            indice = i;
        }
        if (indice != -1) {
          this.active_page.maps.poi[indice].infowindow.close();
          this.active_page.maps.poi[indice].marker.setMap(null);
          this.active_page.maps.poi.splice(indice, 1);
        }
      } else console.error("Remove error!", page, element);
    },
  },
  components: {
    pagebar: httpVueLoader("component/pagebar.vue"),
    sidebar: httpVueLoader("component/sidebar.vue"),
    searchSection: httpVueLoader("component/searchSection.vue"),
    mapSection: httpVueLoader("component/mapSection.vue"),
    graphSection: httpVueLoader("component/graphSection.vue"),
  },
  created: function () {
    this.setActivePage(0);
    this.setActiveSection(0);
  },
};

window.onload = function () {
  // Abilita la ricerca con la pressione del tasto invio
  let input = document.getElementById("search-input-id");
  input.addEventListener("keyup", function (event) {
    if (event.keyCode === 13 || event.key === 13) {
      event.preventDefault();
      document.getElementById("search-button-id").click();
    }
  });

  // Rende la bottom page-bar scrollabile
  document.addEventListener("DOMContentLoaded", function () {
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
  });

  // Close websocket when webpage closes
  window.addEventListener("unload", function (event) {
    if (vm.$data.socket) vm.$data.socket.close();
  });
};
</script>

<style>
:root {
  --sidebar-width: 70px;
  --pagesbar-height: 50px;
  --searchbar-height: 45px;
  --geolocated-sidebar: 400px;
}

#dashboard {
  background-color: rgb(21, 32, 43);
  height: 100vh;
  width: 100vw;
  color: white;
  display: flex;
}

#right-content {
  height: 100%;
  width: calc(100% - var(--sidebar-width));
}

#section-content {
  height: calc(100vh - var(--pagesbar-height));
  width: calc(100vw - var(--sidebar-width));
}

.popover {
  background-color: rgb(19, 30, 41);
  color: white;
  max-width: 350px;
}

.popover_item {
  color: white;
}

.popover-header {
  background-color: rgb(26, 40, 55);
  border-bottom: none;
}

.popover-body {
  color: white;
}

.arrow {
  background-color: transparent;
}

.bs-popover-bottom .arrow::after {
  border-bottom-color: rgb(26, 40, 55);
}

.bs-popover-right .arrow::after {
  border-right-color: rgb(26, 40, 55);
}

label {
  color: white;
  font-size: large;
  margin-top: 5px;
}
</style>
