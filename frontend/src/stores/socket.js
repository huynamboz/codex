// Socket pseudo module for vue-native-sockets
import { defineStore } from "pinia";
import Vue from "vue";

import CHOICES from "@/choices";
import router from "@/router";
import { useAdminStore } from "@/stores/admin";
import { useAuthStore } from "@/stores/auth";
import { useBrowserStore } from "@/stores/browser";
import { useReaderStore } from "@/stores/reader";

const WS_TIMEOUT = 19 * 1000;
const SUBSCRIBE_MESSAGES = {
  admin: JSON.stringify({
    type: "subscribe",
    register: true,
    admin: true,
  }),
  user: JSON.stringify({ type: "subscribe", register: true }),
  unsub: JSON.stringify({ type: "subscribe", register: false }),
};
Object.freeze(SUBSCRIBE_MESSAGES);

const wsKeepAlive = function (ws) {
  if (!ws || ws.readyState !== 1) {
    console.debug("socket not ready, not sending keep-alive.");
    return;
  }
  ws.send("{}");
  setTimeout(() => wsKeepAlive(ws), WS_TIMEOUT);
};

// vue-native-websockets doesn't put socket stuff in its own module :/
export const useSocketStore = defineStore("socket", {
  state: () => ({
    isConnected: false,
    reconnectError: false,
  }),
  actions: {
    SOCKET_ONOPEN(event) {
      Vue.prototype.$socket = event.currentTarget;
      this.$patch((state) => {
        state.isConnected = true;
        state.reconnectError = false;
      });
      try {
        wsKeepAlive(event.currentTarget);
      } catch (error) {
        // Activating the Vue dev console breaks currentTarget
        console.warn("keep-alive", error);
      }
    },
    SOCKET_ONCLOSE() {
      this.isConnected = false;
    },
    SOCKET_ONERROR(event) {
      console.error("socket error", event);
      this.$patch((state) => {
        state.isConnected = false;
        state.reconnectError = true;
      });
    },
    SOCKET_ONMESSAGE(event) {
      // The main message dispatcher.
      // Would be nicer if components could add their own listeners.
      const message = event.data;
      console.debug(message);
      const adminStore = useAdminStore();
      const browserStore = useBrowserStore();
      const readerStore = useReaderStore();

      switch (message) {
        case CHOICES.websockets.LIBRARY_CHANGED:
          browserStore.setTimestamp();
          if (router.currentRoute.name === "browser") {
            browserStore.loadBrowserPage({ showProgress: false });
          }
          readerStore.setTimestamp();

          break;
        case CHOICES.websockets.LIBRARIAN_STATUS:
          adminStore.loadLibrarianStatuses();

          break;
        case CHOICES.websockets.FAILED_IMPORTS:
          adminStore.setFailedImports(true);

          break;
        default:
          console.debug("Unhandled websocket message:", message);
      }
    },
    SOCKET_RECONNECT(count) {
      console.debug("socket reconnect", count);
    },
    SOCKET_RECONNECT_ERROR() {
      console.error("socket reconnect error");
      this.reconnectError = true;
    },
    sendSubscribe() {
      const ws = Vue.prototype.$socket;
      if (!ws || ws.readyState !== 1) {
        console.debug("No ready socket. Not subscribing to notifications.");
        return;
      }
      const authStore = useAuthStore();
      if (authStore.isUserAdmin) {
        ws.send(SUBSCRIBE_MESSAGES.admin);
      }
      if (authStore.isCodexViewable) {
        ws.send(SUBSCRIBE_MESSAGES.user);
      } else {
        ws.send(SUBSCRIBE_MESSAGES.unsub);
      }
    },
  },
});