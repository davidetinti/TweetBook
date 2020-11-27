<template>
  <div id="map-section">
    <!-- Map -->
    <div class="geolocated-sidebar">
      <div class="maps-search-container d-flex flex-column">
        <div
          class="maps-selection-bar d-flex justify-content-between align-items-center px-3"
        >
          <div style="color: rgb(22, 159, 242)">
            <div v-if="page.selected_geo_tweets.length">
              <strong>Selezionati (${page.selected_geo_tweets.length})</strong>
            </div>
          </div>
          <div class="d-flex">
            <div
              @click="() => {}"
              style="color: rgb(22, 159, 242); cursor: pointer"
            >
              <strong>Seleziona tutti</strong>
            </div>
            <div class="px-2">•</div>
            <div
              @click="() => {}"
              style="color: rgb(22, 159, 242); cursor: pointer"
            >
              <strong>Deseleziona tutti</strong>
            </div>
          </div>
        </div>
        <div class="maps-search-tweets-container p-2">
          <div
            class="search-tweets-wrapper"
            v-for="(tweet, index) in geolocalized_tweet"
            :key="index"
          >
            <div class="d-flex px-3 py-2 justify-content-between">
              <div class="d-flex">
                <div class="picture-wrapper">
                  <b-avatar
                    class="mr-2"
                    :src="tweet.user.profile_image_url"
                  ></b-avatar>
                </div>
                <div class="content-wrapper d-flex flex-column">
                  <div class="d-flex flex-wrap">
                    <div class="mr-1">
                      <strong>${tweet.user.name}</strong>
                    </div>
                    <div style="color: rgb(101, 119, 134)">
                      @${tweet.user.screen_name}
                    </div>
                  </div>
                  <div class="tweet-text">${tweet.text}</div>
                </div>
              </div>
              <div class="select-wrapper d-flex align-items-center pl-4">
                <div
                  class="px-2 py-1 checkboxes"
                  @click="toggleSelection(tweet, page.selected_geo_tweets)"
                  style="border-radius: 7px; cursor: pointer"
                  :style="{
                    backgroundColor:
                      page.selected_geo_tweets.indexOf(tweet) != -1
                        ? 'rgb(22, 159, 242)'
                        : 'rgb(101, 119, 134)',
                  }"
                >
                  <div style="width: 13px">
                    ${page.selected_geo_tweets.indexOf(tweet) != -1 ? "✔" : "✘"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div id="map" class="d-flex"></div>
  </div>
</template>

<script>
module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {
      page_copy: null,
      layer: null,
      layers: new google.maps.MVCObject(),
      map: null,
    };
  },
  props: {
    page: Object,
  },
  computed: {
    page_id: function () {
      return this.page ? this.page.id : null;
    },
    page_tweets: function () {
      return this.page ? this.page.tweets : null;
    },
    geolocalized_tweet: function () {
      let array = [];
      this.page.tweets.forEach((tweet) => {
        if (tweet.place) array.push(tweet);
      });
      return array;
    },
  },
  methods: {
    /* Inizializza una mappa all'interno dell'elemento "element */
    initMap(element) {
      let center = {
        lat: 44.456348,
        lng: 11.574575,
      };

      this.map = new google.maps.Map(element, {
        zoom: 4,
        center: center,
        fullscreenControl: false,
        streetViewControl: false,
        mapTypeId: "satellite",
      });
      this.map.addListener("center_changed", () => {
        this.page.maps.lat = this.map.center.lat();
        this.page.maps.lng = this.map.center.lng();
      });
      this.map.addListener("zoom_changed", () => {
        this.page.maps.zoom = this.map.zoom;
      });
    },
    toggleSelection(object, array) {
      if (array.indexOf(object) != -1) {
        array.splice(array.indexOf(object), 1);
        this.removeMarkers(null, this.creationMarkerMap(object, false));
      } else {
        array.push(object);
        this.creationMarkerMap(object, true);
      }
    },
    selectAll() {
      this.deselectAll();
      this.active_page.selected_geo_tweets = this.geolocalized_tweet.slice();
      this.active_page.selected_geo_tweets.forEach((tweet) => {
        this.creationMarkerMap(tweet, true);
      });
    },
    deselectAll() {
      while (this.active_page.maps.poi.length > 0) {
        this.removeMarkers(null, this.active_page.maps.poi[0]);
      }
      this.active_page.selected_geo_tweets = [];
    },
    /* Cerca in un array di oggetti il primo oggetto
        che ha la proprietà "fieldname" pari a "value" */
    /*connectData(fieldname, value, array) {
      return true; // TODO non funziona per streaming, devo sistemare (riccio)
      for (let i = 0; i < array.length; i++) {
        if (array[i][fieldname] == value) return array[i];
      }
    },
    */
    /* Cambia la posizione puntata dalla mappa */
    setMapLocation(lat, lng, zoom) {
      if (this.map) {
        this.map.setCenter({
          lat: lat,
          lng: lng,
        });
        this.map.setZoom(zoom);
      }
    },

    /* Crea heatmap */
    creationHeatMap() {
      var page = this.page.maps;
      page.heat_markers.splice(0, page.heat_markers.length);
      for (let tweet of this.page.tweets) {
        if (tweet.place != null) {
          let lat =
            tweet.place.bounding_box.coordinates[0][1][1] +
            tweet.place.bounding_box.coordinates[0][0][1] +
            tweet.place.bounding_box.coordinates[0][2][1] +
            tweet.place.bounding_box.coordinates[0][3][1];
          let long =
            tweet.place.bounding_box.coordinates[0][1][0] +
            tweet.place.bounding_box.coordinates[0][0][0] +
            tweet.place.bounding_box.coordinates[0][2][0] +
            tweet.place.bounding_box.coordinates[0][3][0];
          lat = lat / 4;
          long = long / 4;
          page.heat_markers.push(new google.maps.LatLng(lat, long));
        }
      }
    },
    reloadHeatMap() {
      if (this.layer != null) this.layer.setMap(null);
      // Reload the map with the new heatmap PoI
      this.layer = new google.maps.visualization.HeatmapLayer({
        data: this.page.maps.heat_markers,
      });
      this.layer.setMap(this.map);
    },
    creationMarkerMap(tweet, insert_into_array) {
      var newpoi = null;
      var result = null;
      if (tweet.place != null) {
        let lat =
          tweet.place.bounding_box.coordinates[0][1][1] +
          tweet.place.bounding_box.coordinates[0][0][1] +
          tweet.place.bounding_box.coordinates[0][2][1] +
          tweet.place.bounding_box.coordinates[0][3][1];
        let long =
          tweet.place.bounding_box.coordinates[0][1][0] +
          tweet.place.bounding_box.coordinates[0][0][0] +
          tweet.place.bounding_box.coordinates[0][2][0] +
          tweet.place.bounding_box.coordinates[0][3][0];
        lat = lat / 4;
        long = long / 4;
        //Creazione POI
        //Marker
        let newmarker = new google.maps.Marker({
          position: new google.maps.LatLng(lat, long),
        });
        //infowindow
        const contentInfoWindow =
          '<div class="d-flex flex-column"  id="content">' +
          "<div>" +
          "<strong>" +
          tweet.user.name +
          "</strong>" +
          "</div>" +
          "<div>" +
          tweet.text +
          "</div>" +
          (typeof tweet.extended_entities !== "undefined"
            ? "<img height='auto' width='220' src='" +
              tweet.extended_entities.media[0].media_url +
              "'>"
            : "") +
          "</div>";
        let newinfowindow = new google.maps.InfoWindow({
          content: contentInfoWindow,
          maxWidth: 250,
        });
        newmarker.addListener("click", () => {
          newinfowindow.open(this.map, newmarker);
        });
        //POI
        newpoi = {
          marker: newmarker,
          infowindow: newinfowindow,
        };
        this.page.maps.poi.push(newpoi);
        if (insert_into_array == true) {
          newpoi.marker.setMap(this.map);
          newpoi.infowindow.open(this.map, newpoi.marker);
          result = this.page.maps.poi[this.page.maps.poi.length - 1];
        } else {
          if (this.page.maps.poi.length > 0) result = this.page.maps.poi.pop();
        }
      }
      return result;
    },
    reloadMarkers(page) {
      //Riscrivo i marker non eliminati nella mappa
      for (poi of page.maps.poi) {
        poi.infowindow.open(this.map, poi.marker);
        poi.marker.setMap(this.map);
      }
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
            this.page.maps.poi[i].infowindow.content
          )
            indice = i;
        }
        if (indice != -1) {
          this.page.maps.poi[indice].infowindow.close();
          this.page.maps.poi[indice].marker.setMap(null);
          this.page.maps.poi.splice(indice, 1);
        }
      } else console.error("Remove error!");
    },
  },
  watch: {
    page(new_value) {
      this.page_copy = new_value;
    },
    // azioni eseguite quando viene cambiata pagine, e quindi cambia il page_id
    page_id(new_value) {
      if (new_value) {
        this.setMapLocation(
          this.page.maps.lat,
          this.page.maps.lng,
          this.page.maps.zoom
        );
        this.reloadHeatMap();
        this.reloadMarkers(this.page);
      }
    },
    page_tweets(new_value) {
      if (new_value) {
        this.creationHeatMap();
        this.reloadHeatMap();
      }
    },
  },
  mounted: function () {
    this.page_copy = this.page;
    this.initMap(document.getElementById("map"));
  },
};
</script>

<style>
#map-section {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.geolocated-sidebar {
  height: calc(100vh - var(--pagesbar-height));
  width: var(--geolocated-sidebar);
}

#map {
  height: 100%;
  width: calc(100% - 200px);
  color: black;
}

.maps-search-container {
  width: var(--geolocated-sidebar);
  height: calc(100vh - var(--pagesbar-height));
  border-right: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.maps-selection-bar {
  height: var(--searchbar-height);
  width: var(--geolocated-sidebar);
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
  font-size: 15px;
}

.maps-search-tweets-container {
  width: var(--geolocated-sidebar);
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  overflow-y: auto;
}

.maps-search-tweets-container::-webkit-scrollbar {
  display: none;
}

.search-tweets-wrapper {
  transition: 0.2s;
  border: 1px solid rgb(47, 51, 54);
  box-sizing: border-box;
  border-radius: 16px;
  width: 100%;
  background-color: rgb(0, 0, 0);
  color: white;
}

.search-tweets-wrapper:hover {
  transition: 0.2s;
  background-color: rgba(18, 21, 23, 0.7);
}
</style>
