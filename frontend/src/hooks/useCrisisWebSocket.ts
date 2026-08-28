import { useEffect } from 'react';
import { connect, getState } from '../services/api';

export function useCrisisWebSocket(
  setState: (state: any) => void,
  onStatus?: (
    status: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING'
  ) => void
) {
  useEffect(() => {
    let socket: WebSocket | undefined;
    let timer: number | undefined;
    let stopped = false;

    const open = () => {
      if (stopped) {
        return;
      }

      onStatus?.('RECONNECTING');

      socket = connect((event) => {
        /*
         * Only refresh the full crisis state when the backend
         * explicitly tells us that the state has changed.
         *
         * Agent activity messages should NOT cause a GET request.
         */
        if (
          event?.type === 'STATE_UPDATED' ||
          event?.type === 'CRISIS_UPDATED' ||
          event?.type === 'PLAN_UPDATED'
        ) {
          getState()
            .then(setState)
            .catch(() => {
              // Ignore temporary refresh failures.
            });
        }
      });

      socket.onopen = () => {
        onStatus?.('CONNECTED');
      };

      socket.onclose = () => {
        if (stopped) {
          return;
        }

        onStatus?.('DISCONNECTED');

        timer = window.setTimeout(() => {
          open();
        }, 2000);
      };

      socket.onerror = () => {
        onStatus?.('DISCONNECTED');
      };
    };

    open();

    return () => {
      stopped = true;

      if (timer) {
        window.clearTimeout(timer);
      }

      socket?.close();
    };
  }, [setState, onStatus]);
}