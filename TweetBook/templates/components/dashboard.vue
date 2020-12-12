    <template>
  <div id="dashboard">
    <!-- Sidebar -->
    <sidebar
      :sections="sections"
      :active_section="active_section"
      @changed-section="setActiveSection"
    ></sidebar>
    <b-overlay
      bg-color="rgb(21, 32, 43)"
      opacity="0.85"
      blur="2px"
      :show="idle_search"
    >
      <!-- Content on the right -->
      <div id="right-content" class="d-flex flex-column">
        <!-- Section content -->
        <div id="section-content">
          <search-section
            v-show="active_section == sections[0]"
            :page="active_page"
            :user="user"
            :valid_mail="validate_mail"
            :newsearch="newsearch"
            @params-update="onParamsUpdate"
            @load-search="onLoadSearch"
            @recent-search-started="idle_search = true"
            @recent-search-done="onRecentSearchDone"
            @toggle-share="onShareSearch"
            @toggle-mail="onMailNotify"
            @search-done="newsearch = false"
            @stream-found="onStreamFound"
            @stream-delete="onStreamDelete"
          >
          </search-section>
          <map-section
            v-show="active_section == sections[1]"
            :page="active_page"
            :to_insert="insert_into_map"
            @inserted="deleteMapInserted"
          ></map-section>
          <graph-section
            v-show="active_section == sections[2]"
            :page="active_page"
            :update_needed="graph_need_update"
            :export="export_graph_promise"
            @graph-updated="graph_need_update = false"
            @related-search="relatedSearch"
          ></graph-section>
          <div id="settings-section" v-show="active_section == setting_section">
            <div id="settings-inner-section">
              <b-button id="twitter-button" v-if="!user" @click="login">
                <em class="fa fa-twitter"></em> Connect Twitter
              </b-button>
              <div
                class="d-flex flex-column align-items-center justify-content-between"
                v-else
              >
                <h3>Account Twitter collegato</h3>
                <div class="d-flex align-items-center px-3 py-2">
                  <img
                    style="border-radius: 50%; height: 4em; width: 4em"
                    :src="getHighQuality(user.profile_image_url)"
                    class="picture-wrapper mx-3"
                  />
                  <div class="content-wrapper d-flex flex-column">
                    <strong>${user.name}</strong>
                    <div style="color: rgb(101, 119, 134)">
                      @${user.screen_name}
                    </div>
                  </div>
                </div>
                <b-button class="mt-3" @click="logout()">Logout</b-button>
              </div>
            </div>
            <div id="settings-inner-section">
              <div
                class="d-flex flex-column align-items-center justify-content-between"
              >
                <h3>Indirizzo E-mail</h3>
                <b-form-input
                  v-model="mail"
                  placeholder="mail..."
                  type="email"
                  :state="validate_mail"
                ></b-form-input>
              </div>
            </div>
          </div>
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
    </b-overlay>
  </div>
</template>

    <script>
module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {
      sections: [
        new Section("searchSection", "Cerca", "fa-search"),
        new Section("mapSection", "Mappa", "fa-map-marker-alt"),
        new Section("graphSection", "Grafici", "fa-chart-bar"),
      ],
      setting_section: new Section("settingSection", "Impostazioni", ""),
      active_page: null,
      pages: [new Page()],
      active_section: null,
      user: null,
      mail: "",
      mail_input_state: null,
      waiting_for_login: false,

      graph_need_update: false,
      export_graph_promise: null,
      newsearch: false,
      insert_into_map: [],
      idle_search: false,
    };
  },
  computed: {
    validate_mail() {
      let mailformat = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
      if (this.mail.match(mailformat)) {
        return true;
      } else {
        return false;
      }
    },
  },
  methods: {
    getHighQuality(url) {
      return url.replace("normal", "400x400");
    },
    login() {
      this.waiting_for_login = true;
      fetch("loginStart/?key=" + Date.now())
        .then((response) => response.json())
        .then((data) => {
          let twitter_login_url = data.url;
          let login_session_key = data.key;
          if (twitter_login_url) {
            let width = Math.max(window.outerWidth * 0.5, 500);
            let height = Math.max(window.outerHeight * 0.8, 500);
            let left = Math.floor(
              window.screenX + (window.outerWidth - width) / 2
            );
            let top = Math.floor(
              window.screenY + (window.outerHeight - height) / 8
            );
            let window_specs =
              "toolbar=0,scrollbars=1,status=1," +
              "resizable=1,location=1,menuBar=0," +
              "left=" +
              left +
              ",top=" +
              top +
              ",width=" +
              width +
              ",height=" +
              height;
            window.open(
              twitter_login_url + "&key=" + login_session_key,
              "_blank",
              window_specs
            );
            let _this = this;
            let interval = setInterval(() => {
              fetch("loginWait/?key=" + login_session_key)
                .then((response) => response.json())
                .then((data) => {
                  if (data.done) {
                    this.setCookie("access_token", data.access_token, 30);
                    this.setCookie(
                      "access_token_secret",
                      data.access_token_secret,
                      30
                    );
                    this.fetchUserData();
                    clearInterval(interval);
                  }
                });
            }, 2 * 1000);
            setTimeout(() => clearInterval(interval), 120 * 1000);
          } else {
            window.alert("Impossibile effettuare il login in questo momento");
          }
        });
    },
    logout() {
      this.setCookie("access_token", "", 0);
      this.setCookie("access_token_secret", "", 0);
      this.user = null;
      this.pages.forEach((page) => {
        let share = page.search_parameters.share;
        share.hours = 0;
        share.mins = 0;
        share.active = false;
        clearInterval(share.interval);
      });
    },
    setActiveSection(index) {
      if (index >= 0 && index < this.sections.length) {
        this.active_section = this.sections[index];
      } else if (index == -1) {
        this.active_section = this.setting_section;
      }
    },
    // può essere chiamata sia con l'oggetto che con l'indice
    setActivePage(val) {
      if (this.active_page) this.removeMarkers(this.active_page, null);
      switch (typeof val) {
        case "number":
          if (val >= 0 && val < this.pages.length) {
            this.active_page = this.pages[val];
            this.graph_need_update = true;
          }
          break;
        case "object":
          this.active_page = val;
          this.graph_need_update = true;
          break;
        default:
          break;
      }
    },
    addPage(page) {
      if (this.active_page) this.removeMarkers(this.active_page, null);
      this.pages.push(page ? page : new Page());
      this.setActivePage(this.pages.length - 1);
    },
    removePage(index) {
      if (this.pages.length > 1) {
        let removed_current_page =
          index == this.pages.indexOf(this.active_page);
        this.removeMarkers(this.pages[index], null);
        this.pages.splice(index, 1);
        if (removed_current_page) {
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
      while (this.active_page.maps.poi.length > 0) {
        page.maps.poi[0].infowindow.close();
        page.maps.poi[0].marker.setMap(null);
        page.maps.poi.shift();
      }
      page.maps = new MapParameters();
      page.selected_tweets = [];
      page.selected_geo_tweets = [];
      page.graphs = {};
      this.graph_need_update = true;
      this.idle_search = false;
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
    fetchUserData() {
      let access_token = this.getCookie("access_token");
      let access_token_secret = this.getCookie("access_token_secret");
      if (access_token && access_token_secret) {
        fetch(
          "getUserData/?access_token=" +
            access_token +
            "&access_token_secret=" +
            access_token_secret
        )
          .then((response) => response.json())
          .then((data) => (this.user = data));
      }
    },
    // setto l'intervallo
    onMailNotify(page){
      let index = this.pages.indexOf(page);
      let active = this.pages[index].search_parameters.mail.active;
      let hours = this.pages[index].search_parameters.mail.hours;
      let mins = this.pages[index].search_parameters.mail.mins;
      let interval = this.pages[index].search_parameters.mail.interval;
      if (active) {
        this.pages[index].last_mail_id = this.pages[index].tweets[0].id;
        this.pages[index].search_parameters.mail.interval = setInterval(() => {
          this.sendMail(index);
        }, (hours * 60 + mins) * 60 * 1000);
      } else {
        clearInterval(this.pages[index].search_parameters.mail.interval);
      }
    },
    // l'intervallo scade
    sendMail(index){
      if (this.pages[index].last_mail_id != this.pages[index].tweets[0].id){
        this.pages[index].last_mail_id = this.pages[index].tweets[0].id;
        fetch("sendMail/?mail=" + this.mail)
        .then((response) => response.json())
          .then((data) => {
            if (!data.ok)
              clearInterval(this.pages[index].search_parameters.mail.interval);
          });
      }
    },
    onShareSearch(page) {
      let index = this.pages.indexOf(page);
      let active = this.pages[index].search_parameters.share.active;
      let hours = this.pages[index].search_parameters.share.hours;
      let mins = this.pages[index].search_parameters.share.mins;
      let interval = this.pages[index].search_parameters.share.interval;
      if (active) {
        this.pages[index].search_parameters.share.interval = setInterval(() => {
          this.shareSearch(index);
        }, (hours * 60 + mins) * 60 * 1000);
      } else {
        clearInterval(this.pages[index].search_parameters.share.interval);
      }
    },
    deleteMapInserted(tweets) {
      for (tweet of tweets) {
        var index = this.insert_into_map.indexOf(tweet);
        this.insert_into_map.splice(index, 1);
      }
    },
    onStreamFound(tweet) {
      this.idle_search = false;
    },
    onStreamDelete(tweet) {},
    shareSearch(index) {
      let access_token = this.getCookie("access_token");
      let access_token_secret = this.getCookie("access_token_secret");
      if (access_token && access_token_secret) {
        /*
                        //Graphs
                        new Promise((resolve) => {
                          this.export_graph_promise = resolve;
                        }).then((chart_pie, chart_bar, word_cloud) => {
                          //Map
                          let map_url = this.staticMapUrl(index);
                        });
                        */
        let map_url = this.staticMapUrl(index);
        fetch(
          "postStatus/?access_token=" +
            access_token +
            "&access_token_secret=" +
            access_token_secret +
            "&map_url=" +
            map_url
        )
          .then((response) => response.json())
          .then((data) => {
            if (!data.ok)
              clearInterval(this.pages[index].search_parameters.share.interval);
          });
      }
    },
    staticMapUrl(index) {
      let page = this.pages[index];
      let markers = [];
      page.tweets.forEach((tweet) => {
        if (tweet.place || tweet.places) markers.push(tweet);
      });

      //URL of Google Static Maps.
      let static_map_url = "https://maps.googleapis.com/maps/api/staticmap?";

      //Set the Google Map Size.
      static_map_url += "size=1080x1080" + "&";
      //Set the Google Map Scale.
      static_map_url += "scale=2" + "&";
      //Set the Google Map Type.
      static_map_url += "maptype=hybrid" + "&";

      if (!markers.length) {
        //Set the Google Map Center.
        static_map_url += "center=" + page.maps.lat + "," + page.maps.lng + "&";
        //Set the Google Map Zoom.
        static_map_url += "zoom=" + page.maps.zoom;
      } else {
        //Loop and add Markers
        static_map_url += "&markers=";
        markers.forEach((marker) => {
          let object = this.getCoordinates(marker);
          static_map_url += "|" + object.lat + "," + object.lng;
        });
      }

      //Set the Google Map Static API key.
      static_map_url += "&key=AIzaSyAvzBELeBcb9qY53VlDrUIhYWZ5-hroTJ0";
      console.log(static_map_url);
      return encodeURIComponent(static_map_url);
    },
    getCoordinates(tweet) {
      let lat, long;
      if (tweet.place) {
        lat =
          tweet.place.bounding_box.coordinates[0][1][1] +
          tweet.place.bounding_box.coordinates[0][0][1] +
          tweet.place.bounding_box.coordinates[0][2][1] +
          tweet.place.bounding_box.coordinates[0][3][1];
        long =
          tweet.place.bounding_box.coordinates[0][1][0] +
          tweet.place.bounding_box.coordinates[0][0][0] +
          tweet.place.bounding_box.coordinates[0][2][0] +
          tweet.place.bounding_box.coordinates[0][3][0];
        lat = lat / 4;
        long = long / 4;
      } else if (tweet.places) {
        lat = (tweet.places[0].geo.bbox[1] + tweet.places[0].geo.bbox[3]) / 2;
        long = (tweet.places[0].geo.bbox[0] + tweet.places[0].geo.bbox[2]) / 2;
      }
      return { lat: lat, lng: long };
    },
    getCookie(cname) {
      var name = cname + "=";
      var decodedCookie = decodeURIComponent(document.cookie);
      var ca = decodedCookie.split(";");
      for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == " ") {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return null;
    },
    setCookie(cname, cvalue, exdays) {
      var d = new Date();
      d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
      var expires = "expires=" + d.toUTCString();
      document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    },
    //start new search when clicked on termcloud
    relatedSearch(e) {
      let keyword = e.target.dataItem.dataContext.word;
      let newPage = new Page();
      newPage.search_parameters.keywords = keyword;
      this.addPage(newPage);
      this.active_section = this.sections[0];
      this.newsearch = true;
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
    let vue = this;
    this.setActivePage(0);
    this.setActiveSection(0);
    this.graph_need_update = false;
    // Close websocket when webpage closes
    window.addEventListener("unload", function (event) {
      if (vue.socket) {
        window.open("http://www.google.com");
        vue.socket.close();
      }
    });
  },
  mounted: function () {
    this.fetchUserData();
  },
};

window.onload = function () {
  // Abilita la ricerca con la pressione del tasto invio
  let input = document.getElementById("search-input-id");
  input.addEventListener("keyup", function (event) {
    if (event.keyCode === 13 || event.key === 13) {
      try {
        event.preventDefault();
      } catch (error) {
        console.error("Prevent default error: " + error);
      }
      document.getElementById("search-button-id").click();
    }
  });
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

#settings-section {
  height: 100%;
  width: 100%;
  display: flex;
}

#settings-inner-section {
  height: 100%;
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

#twitter-button {
  background-color: rgb(22, 159, 242);
  color: white;
  border: none;
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

.text-dark {
  color: #ffffff !important;
}

.b-sidebar {
  background-color: rgb(21, 32, 43) !important;
}

label {
  color: white;
  font-size: large;
  margin-top: 5px;
}
</style>
