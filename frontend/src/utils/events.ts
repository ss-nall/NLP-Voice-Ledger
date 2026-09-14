import { useEffect } from 'react';

export const LEDGER_UPDATED_EVENT = 'nlpledger:ledger_updated';

export const notifyLedgerUpdated = () => {
  window.dispatchEvent(new CustomEvent(LEDGER_UPDATED_EVENT));
};

export const useLedgerUpdated = (callback: () => void) => {
  useEffect(() => {
    const handleUpdate = () => {
      callback();
    };
    window.addEventListener(LEDGER_UPDATED_EVENT, handleUpdate);
    return () => {
      window.removeEventListener(LEDGER_UPDATED_EVENT, handleUpdate);
    };
  }, [callback]);
};
