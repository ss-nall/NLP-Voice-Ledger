/**
 * Offline Transaction Queue & Auto-Sync Engine for PWA.
 * Queues transactions when network or backend is unreachable,
 * and automatically drains & synchronizes upon reconnection.
 */

import { api } from '../api/client';
import { notifyLedgerUpdated } from './events';

export interface QueuedTransaction {
  id: string;
  messageText: string;
  sessionId: string;
  timestamp: string;
  isVoice?: boolean;
  status: 'PENDING' | 'SYNCING' | 'FAILED';
  retryCount: number;
}

const STORAGE_QUEUE_KEY = 'nlpledger_offline_tx_queue_v1';

export class OfflineQueueService {
  private static instance: OfflineQueueService;
  private queue: QueuedTransaction[] = [];
  private isSyncing: boolean = false;
  private listeners: ((queue: QueuedTransaction[]) => void)[] = [];

  private constructor() {
    this.loadQueue();
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        console.log("🌐 Network online detected, initiating auto-sync...");
        this.drainQueue();
      });
    }
  }

  public static getInstance(): OfflineQueueService {
    if (!OfflineQueueService.instance) {
      OfflineQueueService.instance = new OfflineQueueService();
    }
    return OfflineQueueService.instance;
  }

  private loadQueue() {
    try {
      const saved = localStorage.getItem(STORAGE_QUEUE_KEY);
      if (saved) {
        this.queue = JSON.parse(saved);
      }
    } catch (e) {
      console.warn("Failed to load offline queue:", e);
      this.queue = [];
    }
  }

  private saveQueue() {
    try {
      localStorage.setItem(STORAGE_QUEUE_KEY, JSON.stringify(this.queue));
      this.notifyListeners();
    } catch (e) {
      console.warn("Failed to persist offline queue:", e);
    }
  }

  public subscribe(listener: (queue: QueuedTransaction[]) => void): () => void {
    this.listeners.push(listener);
    listener(this.getPendingItems());
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners() {
    const items = this.getPendingItems();
    this.listeners.forEach(l => l(items));
  }

  public enqueue(messageText: string, sessionId: string, isVoice: boolean = false): QueuedTransaction {
    const item: QueuedTransaction = {
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      messageText,
      sessionId,
      timestamp: new Date().toISOString(),
      isVoice,
      status: 'PENDING',
      retryCount: 0
    };
    this.queue.push(item);
    this.saveQueue();

    // If online, attempt immediate sync
    if (navigator.onLine) {
      this.drainQueue();
    }
    return item;
  }

  public getPendingItems(): QueuedTransaction[] {
    return this.queue.filter(i => i.status === 'PENDING' || i.status === 'FAILED');
  }

  public getQueueCount(): number {
    return this.getPendingItems().length;
  }

  public async drainQueue(): Promise<{ synced: number; failed: number }> {
    if (this.isSyncing || this.getPendingItems().length === 0) {
      return { synced: 0, failed: 0 };
    }

    this.isSyncing = true;
    let synced = 0;
    let failed = 0;

    const pending = [...this.getPendingItems()];
    for (const item of pending) {
      item.status = 'SYNCING';
      this.saveQueue();

      try {
        const res = item.isVoice
          ? await api.processSpokenText(item.messageText, item.sessionId)
          : await api.sendMessage(item.messageText, item.sessionId);
        if (res && res.success !== false) {
          // Successfully synced! Remove from queue
          this.queue = this.queue.filter(q => q.id !== item.id);
          synced++;
        } else {
          item.status = 'FAILED';
          item.retryCount++;
          failed++;
        }
      } catch (err) {
        console.warn(`Sync failed for item ${item.id}:`, err);
        item.status = 'FAILED';
        item.retryCount++;
        failed++;
      }
      this.saveQueue();
    }

    this.isSyncing = false;
    if (synced > 0) {
      notifyLedgerUpdated();
    }
    return { synced, failed };
  }

  public clearQueue() {
    this.queue = [];
    this.saveQueue();
  }
}

export const offlineQueue = OfflineQueueService.getInstance();
