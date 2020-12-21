<template>
  <div id="search-section">
    <!-- Searchbar -->
    <div class="searchbar d-flex justify-content-between">
      <div class="d-flex align-items-center">
        <b-button
          class="advanced-search-button ml-4 mr-2"
          id="advanced-filter-activator"
          @click="map_popover_open = false"
        >
          <em class="fas fa-sliders-h"></em>
        </b-button>

        <b-form-input
          autocomplete="off"
          id="search-input-id"
          class="search-input mx-2"
          placeholder="Ricerca..."
          spellcheck="false"
          type="text"
          @input="onInput()"
          v-model="page_copy.search_parameters.keywords"
        ></b-form-input>

        <b-button
          id="search-button-id"
          class="search-button mx-2"
          @click="search()"
        >
          <em class="fas fa-search"></em>
        </b-button>

        <b-button
          v-show="stream_connection_open"
          variant="danger"
          @click="closeStreamConnection()"
        >
          Ferma streaming
        </b-button>
      </div>
      <div class="d-flex align-items-center">
        <b-button
          v-show="page_copy.search_parameters.stream"
          class="share-search-button mx-2"
          id="send-mail-activator"
        >
          <em class="fas fa-envelope"></em>
        </b-button>
        <b-button
          v-show="user"
          class="share-search-button mx-2"
          id="share-search-activator"
        >
          <em class="fas fa-share-square"></em>
        </b-button>
        <b-button
          @click="saveSearch(page)"
          class="search-button mx-2"
          id="download-button"
        >
          Download
          <em class="fas fa-file-download"></em>
        </b-button>

        <b-button
          @click="openFileSelector()"
          class="search-button ml-2 mr-4"
          id="upload-button"
        >
          Upload
          <em class="fas fa-file-upload"></em>
        </b-button>
        <b-form-file
          id="upload-form-file"
          accept=".json"
          multiple
          plain
          v-model="loaded_files"
          @input="onFileInput"
          style="display: none"
        ></b-form-file>
      </div>
    </div>

    <!-- Empty search -->
    <div v-if="!page.name" class="search-empty">
      <em class="far fa-sticky-note fa-3x"></em>
      <h3>Nessuna ricerca effettuata...</h3>
    </div>
    <!-- Search done -->
    <div v-else class="search-done">
      <div class="search-tweets-container p-2">
        <div
          @click="showTweet(tweet.id_str)"
          class="search-tweets-wrapper"
          v-for="(tweet, index) in page.tweets"
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
          </div>
        </div>
      </div>
      <div class="extra-content-wrapper">
        <!-- Images -->
        <div id="images" class="images-wrapper no-scrollbar d-flex flex-wrap">
          <div
            v-for="(media, index) in current_page_media"
            :key="index"
            class="image-container-parent"
          >
            <div
              class="image-container-child d-flex align-items-center justify-content-center"
              :style="{ backgroundImage: 'url(' + media.url + ')' }"
              @click="showTweet(media.tweet_id)"
            ></div>
          </div>
        </div>
        <!-- Tweet Lookup -->
        <div
          id="tweet-lookup-wrapper"
          class="p-2 tweet-lookup-wrapper no-scrollbar"
        >
          <div
            id="tweet-lookup"
            class="tweet-lookup-container d-flex align-items-center flex-column"
          >
            <p style="text-align: center" class="my-auto">
              Seleziona un tweet per vederne i dettagli
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Avenced search popup -->
    <b-popover
      target="advanced-filter-activator"
      triggers="click blur"
      placement="topright"
      class="popover"
      ref="popover"
    >
      <template #title>
        <h3 class="mx-1 mt-1" style="color: white">Ricerca avanzata</h3>
      </template>
      <div class="d-flex">
        <div class="d-flex flex-column mb-2 mx-1">
          <b-form-checkbox
            id="stream-checkbox"
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.stream"
            :disabled="currently_streaming"
          >
            Ricerca in streaming
          </b-form-checkbox>
          <div style="color: white; font-size: large">Includi</div>
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.retweets"
          >
            Retweet
          </b-form-checkbox>
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.replies"
          >
            Risposte
          </b-form-checkbox>
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.only_geolocated"
          >
            Solo geolocalizzati
          </b-form-checkbox>
          <label for="input-utente">Utente</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-utente"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.user"
          ></b-form-input>
          <label for="input-luogo"
            >Luogo
            <em @click="openDrawMap" class="fas fa-drafting-compass"></em>
          </label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-luogo"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.location"
          ></b-form-input>
          <label for="input-hashtag">Hashtag</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-hashtag"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.hashtag"
          ></b-form-input>
          <label for="input-tag">Tag</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-tag"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.tag"
          ></b-form-input>
        </div>
        <div id="search-map" style="width: 0px"></div>
      </div>
    </b-popover>

    <!-- Send mail popup -->
    <b-popover
      target="send-mail-activator"
      triggers="click blur"
      placement="topright"
      class="popover"
      ref="popover"
    >
      <div v-if="!valid_mail">
        Inserisci una mail valida per ricevere aggironamenti
      </div>
      <div v-else class="d-flex flex-column mb-2 mx-1">
        <div>Notificami nuovi risultati ogni</div>
        <div class="my-3 d-flex justify-content-around align-items-center">
          <b-form-select
            class="search-input"
            :options="hour_options"
            :disabled="page_copy.search_parameters.mail.active"
            @input="onInput()"
            v-model="page_copy.search_parameters.mail.hours"
            style="width: 80px"
          ></b-form-select>
          <div class="mx-2">ore</div>
          <b-form-select
            class="search-input"
            :options="min_options"
            :disabled="page_copy.search_parameters.mail.active"
            @input="onInput()"
            v-model="page_copy.search_parameters.mail.mins"
            style="width: 80px"
          ></b-form-select>
          <div class="ml-2">minuti</div>
        </div>
        <b-button
          class="align-self-center"
          style="width: 100%"
          @click="toggleMail()"
        >
          ${page_copy.search_parameters.mail.active ? "Disattiva" : "Attiva"}
        </b-button>
      </div>
    </b-popover>

    <!-- Share search popup -->
    <b-popover
      target="share-search-activator"
      triggers="click blur"
      placement="topright"
      class="popover"
      ref="popover"
    >
      <div v-if="!user">Connetti il tuo profilo per condividere i dati</div>
      <div v-else class="d-flex flex-column mb-2 mx-1">
        <div>Condividi i dati su Twitter ogni</div>
        <div class="my-3 d-flex justify-content-around align-items-center">
          <b-form-select
            class="search-input"
            id="hours"
            :disabled="page_copy.search_parameters.share.active"
            @input="onInput()"
            :options="hour_options"
            v-model="page_copy.search_parameters.share.hours"
            style="width: 80px"
          ></b-form-select>
          <div class="mx-2">ore</div>
          <b-form-select
            class="search-input"
            id="minutes"
            :disabled="page_copy.search_parameters.share.active"
            @input="onInput()"
            :options="min_options"
            v-model="page_copy.search_parameters.share.mins"
            style="width: 80px"
          ></b-form-select>
          <div class="ml-2">minuti</div>
        </div>
        <b-button
          class="align-self-center"
          style="width: 100%"
          @click="toggleShare()"
        >
          ${page_copy.search_parameters.share.active ? "Disattiva" : "Attiva"}
        </b-button>
      </div>
    </b-popover>
  </div>
</template>

<script>
module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {
      loaded_files: [],
      page_copy: null,
      socket: null,
      stream_connection_open: false,
      changing_stream_query: false,
      min_options: [0,1,2,3,4,5,10,15,20,30,45],
      hour_options: [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
      ],
      map: null,
      map_circle: null,
      drawing_manager: null,
      map_popover_open: false,
    };
  },
  props: {
    page: Object,
    user: Object,
    valid_mail: Boolean,
    newsearch: Boolean,
  },
  mounted: function () {
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
  },
  computed: {
    /* Media della ricerca attuale */
    current_page_media: function () {
      let array = [];
      this.page.tweets.forEach((tweet) => {
        if (tweet.extended_entities) {
          tweet.extended_entities.media.forEach((media) => {
            array = array.concat({
              url: media.media_url,
              tweet_id: tweet.id_str,
            });
          });
        }
      });
      return array;
    },
    currently_streaming: function () {
      return (
        this.stream_connection_open && this.page_copy.search_parameters.stream
      );
    },
  },
  methods: {
    openDrawMap() {
      if(this.map_popover_open){
        this.map_popover_open = false;
        document.getElementById("search-map").style.width = "0px";
      }else{
        this.map_popover_open = true;
        document.getElementById("search-map").style.width = "300px";
      } 
      
      let element = document.getElementById("search-map");
      let center = {
        lat: 44.456348,
        lng: 11.574575,
      };

      this.map = new google.maps.Map(element, {
        zoom: 4,
        center: center,
        mapTypeControl: false,

        fullscreenControl: false,
        streetViewControl: false,
        mapTypeId: "satellite",
      });
      console.log(this.map)
      this.initDrawingManager();
      google.maps.event.addListener(this.drawing_manager, 'circlecomplete', this.updateCircle);
    },
    initDrawingManager() {
      this.drawing_manager = new google.maps.drawing.DrawingManager({
        drawingMode: google.maps.drawing.OverlayType.MARKER,
        drawingControl: true,
        drawingControlOptions: {
          position: google.maps.ControlPosition.TOP_CENTER,
          drawingModes: [
            //google.maps.drawing.OverlayType.MARKER,
            google.maps.drawing.OverlayType.CIRCLE,
          ],
        },
        markerOptions: {
          icon:
            "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png",
        },
        circleOptions: {
          fillColor: "#00ff00",
          strokeColor: "#56d800",
          clickable: false,
          editable: true,
          zIndex: 1,
        },
      });
      this.drawing_manager.setMap(this.map);
      
    },
    updateCircle(circle) {
      if (this.map_circle) this.map_circle.setMap(null);
      this.map_circle = null;
      this.map_circle = circle;
      this.page.search_parameters.location =
          `${circle.center.lat()},${circle.center.lng()},${circle.radius/1000}km`;
    },
    toggleMail() {
      if (
        this.page_copy.search_parameters.mail.hours ||
        this.page_copy.search_parameters.mail.mins
      ) {
        this.page_copy.search_parameters.mail.active = !this.page_copy
          .search_parameters.mail.active;
        this.onInput();
        this.$emit("toggle-mail", this.page);
      }
    },
    toggleShare() {
      if (
        this.page_copy.search_parameters.share.hours ||
        this.page_copy.search_parameters.share.mins
      ) {
        this.page_copy.search_parameters.share.active = !this.page_copy
          .search_parameters.share.active;
        this.onInput();
        this.$emit("toggle-share", this.page);
      }
    },
    search() {
      /* Salvo la pagina in una variabile per tenerne	
                traccia nel caso prima che la ricerca finisca	
                viene cambiata pagina */
      let page = this.page;
      let params = this.page.search_parameters;
      let parameters = this.getPageName(
        params.keywords,
        params.user,
        params.location,
        params.hashtag,
        params.tag
      );
      if (parameters !== "") {
        this.$emit("recent-search-started");
        if (params.stream) {
          this.oldapi = false;
          this.streamTweets(params.keywords);
          return;
        }
        this.oldapi = true;
        let url =
          "search/?keywords=" +
          encodeURIComponent(params.keywords) +
          "&retweets=" +
          encodeURIComponent(params.retweets) +
          "&replies=" +
          encodeURIComponent(params.replies) +
          "&only_geolocated=" +
          encodeURIComponent(params.only_geolocated) +
          "&user=" +
          encodeURIComponent(params.user) +
          "&location=" +
          encodeURIComponent(params.location) +
          "&hashtag=" +
          encodeURIComponent(params.hashtag) +
          "&tag=" +
          encodeURIComponent(params.tag);
        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            page.tweets = data.statuses;
            page.name = parameters;
            this.$emit("recent-search-done", page);
            /* DEBUG */
            console.log("Data:");
            console.log(data);
          });
      } else {
        window.alert("Inserisci almeno un parametro valido di ricerca.");
      }
    },
    streamTweets(keywords) {
      let vue = this;
      this.$emit("recent-search-started");
      let page = this.page;
      let params = this.page.search_parameters;
      page.name = this.getPageName(
        params.keywords,
        params.user,
        params.location,
        params.hashtag,
        params.tag
      );
      page.tweets = [];
      page.matching_rules = [];
      page.includes = [];
      params = page.search_parameters;
      keywords = this.getStreamQuery(keywords, params);
      console.log("Search keywords: " + keywords);

      // Send keywords into websocket connection
      if (!this.stream_connection_open) {
        console.log("Prima ricerca stream");
        this.stream_connection_open = true;
        this.socket = new WebSocket(
          "ws://" + window.location.hostname + ":5000"
        );
        this.socket.onopen = () => this.socket.send(keywords);
      } else {
        console.log("Ricerca stream dopo la prima");
        page.tweets = [];
        this.socket.send(keywords);
        this.changing_stream_query = true;
      }

      // Update page on tweet received from streaming
      this.socket.addEventListener("message", function (event) {
        if (!page.search_parameters.stream) return;

        let tweet = vue.adjustTweetFormat(JSON.parse(event.data));
        /*if (vue.changing_stream_query) {
          console.log('Sto cambiando. Regola di questo tweet: ', tweet.matching_rules[0].id) // TODO per fermare la visualizzazione dello stream appena cambio la query dello streaming, fino a che non arriva qualcosa secondo le nuove regoleif (this.changing_stream_query) {
          var page_rules = JSON.parse(JSON.stringify(page.matching_rules)); // TODO non serve tutta la pagina, quando sono sicuro al 100% che funziona prendi solo il primo elemento (ultima regola in ordine temporale)
          console.log('Vecchia regola: ', page_rules, page_rules[0]);
          let tweet_with_new_rule_found = (tweet.matching_rules[0].id != page_rules[0])
          if (tweet_with_new_rule_found){
            this.changing_stream_query = false;
            console.log('OK, new/old rule: ', tweet.matching_rules[0].id, page.matching_rules[0]);  
          }
          else {
            console.log('NON OK, new/old rule: ', tweet.matching_rules[0].id, page.matching_rules[0]);
            return;
          }
        }*/
        vue.$emit("stream-found", tweet);
        page.tweets.unshift(tweet);
        page.matching_rules.unshift(tweet.matching_rules[0].id);

        if (page.tweets.length > 100) {
          vue.$emit("stream-delete", page.tweets.pop());
          page.matching_rules.pop();
        }
      });
    },
    getPageName(keywords, utente, luogo, hashtag, tag) {
      let name = "";
      if (keywords !== "") name = keywords;
      else if (hashtag !== "") name = hashtag;
      else if (tag !== "") name = tag;
      else if (utente !== "") name = utente;
      else if (luogo !== "") name = luogo;
      return name;
    },
    getStreamQuery(keywords, params) {
      keywords =
        keywords +
        (params.retweets ? " " : " -is:retweet") +
        (params.replies ? " " : " -is:reply") +
        (params.user == "" ? " " : " from:" + params.user) +
        (params.hashtag == "" ? " " : " #" + params.hashtag) +
        (params.tag == "" ? " " : " @" + params.tag) +
        " !EXTRA_TAG!" +
        (params.only_geolocated ? " -is:geo" : "") +
        (params.location == "" ? " " : " location:" + params.location);
      return keywords;
    },
    adjustTweetFormat(tweet) {
      console.log(tweet);
      tweet.data.id_str = tweet.data.id;
      tweet.data.user = tweet.includes.users[0];
      tweet.data.user.screen_name = tweet.data.user.username;
      tweet.data.places = tweet.includes.places;
      tweet.data.matching_rules = tweet.matching_rules;

      if (tweet.includes.media) {
        tweet.data.extended_entities = {};
        tweet.data.extended_entities.media = tweet.includes.media.map(function (media) {
          media.media_url = media.url ? media.url : media.preview_image_url
          delete media.url;
          return media;
        });
      }
      return tweet.data;
    },
    /* Mostra nel pannello il tweet corrispondente a "tweet_id" */
    showTweet(tweet_id) {
      let tweet_wrapper = document.getElementById("tweet-lookup");
      if (tweet_wrapper && tweet_id) {
        /* Clear the tweet lookup panel */
        while (tweet_wrapper.hasChildNodes()) {
          tweet_wrapper.removeChild(tweet_wrapper.lastChild);
        }
        /* Create the spinner for the tweet lookup panel */
        let opts = {
          lines: 12, // The number of lines to draw
          length: 38, // The length of each line
          width: 17, // The line thickness
          radius: 45, // The radius of the inner circle
          scale: 0.4, // Scales overall size of the spinner
          corners: 1, // Corner roundness (0..1)
          speed: 1, // Rounds per second
          rotate: 0, // The rotation offset
          animation: "spinner-line-fade-quick", // The CSS animation name for the lines
          direction: 1, // 1: clockwise, -1: counterclockwise
          color: "#ffffff", // CSS color or array of colors
          fadeColor: "transparent", // CSS color or array of colors
          top: "50%", // Top position relative to parent
          left: "0%", // Left position relative to parent
          shadow: "0 0 1px transparent", // Box-shadow for the lines
          className: "spinner", // The CSS class to assign to the spinner
          position: "relative", // Element positioning
        };
        new Spin.Spinner(opts).spin(tweet_wrapper);
        /* Start the lookup */
        twttr.widgets
          .createTweet(tweet_id, tweet_wrapper, {
            theme: "dark",
            lang: "it",
          })
          .then(() => {
            tweet_wrapper.removeChild(tweet_wrapper.firstChild);
            tweet_wrapper.firstChild.style["display"] = "block";
          });
      }
    },
    /* Scarica un file JSON di 'page' */
    saveSearch(page) {
      if (page.tweets.length) {
        let data = JSON.stringify(page);
        let blob = new Blob([data], {
          type: "application/json",
        });
        let filename = page.name;
        let link = document.createElement("a");
        link.download = filename;
        //Funzione createObjectURL cross-browser
        let createObjectURL =
          (window.URL || window.webkitURL || {}).createObjectURL ||
          function () {};
        link.href = createObjectURL(blob);
        link.click();
      }
    },
    /* Aggiunge una nuova pagina contenente i dati del file
        al percorso "file" */
    loadSearch(file) {
      if (file) {
        let path = file;
        let fileReader = new FileReader();
        let _this = this;
        fileReader.onload = function (event) {
          try {
            let text = event.target.result;
            let json = JSON.parse(text);
            if (_this.jsonFileErrors(json)) {
              throw "jsonshemeerror";
            }
            _this.$emit("load-search", json);
          } catch (err) {
            if (err == "jsonschemeerror")
              window.alert("file .json non contenente tweet");
            else window.alert("Il file deve essere di tipo JSON!");
          }
        };
        fileReader.readAsText(path, "utf-8");
      } else {
        window.alert("Inserire un file da caricare");
      }
    },
    openFileSelector() {
      document.getElementById("upload-form-file").click();
    },
    /* Funzione che va a controllare l'integrità dell'oggetto page */
    jsonFileErrors(json) {
      if (!json.hasOwnProperty("name")) return true;
      if (!json.hasOwnProperty("tweets")) return true;
      if (!json.hasOwnProperty("search_parameters")) return true;
      //if (!json.hasOwnProperty('selected_images')) return true;
      return false;
    },
    onInput() {
      this.$emit("params-update", this.page_copy.search_parameters);
    },
    onFileInput() {
      for (let i = 0; i < this.loaded_files.length; i++) {
        this.loadSearch(this.loaded_files[i]);
      }
      this.loaded_files = [];
    },
    closeStreamConnection() {
      if (this.socket) {
        console.log("Connessione in streaming chiusa (era aperta)");
        this.stream_connection_open = false;
        this.socket.close();
      }
    },
  },
  watch: {
    /* When prop is updated, the value is stored into the copy */
    page(new_value) {
      this.page_copy = new_value;
    },
    newsearch(new_value) {
      if (new_value) {
        this.search();
        this.$emit("search-done");
      }
    },
  },
  created: function () {
    this.page_copy = this.page;
    // Close websocket when webpage closes
    window.addEventListener("unload", this.closeStreamConnection);
  },
};
</script>

<style>
#search-section {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.searchbar {
  height: var(--searchbar-height);
  width: calc(100vw - var(--sidebar-width));
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.advanced-search-button {
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 20px;
}

.advanced-search-button * {
  color: rgb(22, 159, 242);
}

.search-input {
  background-color: rgb(37, 51, 65);
  border-radius: 22px;
  width: 300px;
  height: 70%;
  border: 1px solid rgba(0, 0, 0, 0);
  box-sizing: border-box;
  color: white;
}

.search-input:focus {
  background-color: rgba(0, 0, 0, 0);
  border-color: rgb(29, 161, 242);
  color: white;
}

.search-button {
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 20px;
}

.search-button * {
  color: #aab8c2;
}

.search-empty {
  display: flex;
  flex-direction: column;
  width: calc(100vw - var(--sidebar-width));
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  justify-content: center;
  align-items: center;
}

.search-done {
  display: flex;
  width: calc(100vw - var(--sidebar-width));
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  color: white;
}

.selection-bar {
  height: var(--searchbar-height);
  width: calc((100vw - var(--sidebar-width)) / 2);
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.search-tweets-container {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  border-right: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
  overflow-y: auto;
}

.search-tweets-container::-webkit-scrollbar {
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

.extra-content-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  display: flex;
  flex-direction: column;
}

.images-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
  overflow-y: auto;
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.image-container-parent {
  width: calc((100vw - var(--sidebar-width)) / 6);
  height: calc((100vw - var(--sidebar-width)) / 6);
  padding: 5px;
}

.image-container-child {
  height: 100%;
  width: 100%;
  transition: 0.2s;
  background-color: rgb(0, 0, 0);
  border: 1px solid rgb(47, 51, 54);
  box-sizing: border-box;
  border-radius: 16px;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  cursor: pointer;
}

.image-container-child:hover {
  transition: 0.2s;
  background-color: rgba(18, 21, 23, 0.7);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.tweet-text {
  line-height: 1.3125;
}

.popover {
  max-width: 600px;
}

.tweet-lookup-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
  overflow-y: auto;
}

.tweet-lookup-container {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
}
</style>
