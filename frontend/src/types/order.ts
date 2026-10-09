
export interface OrderItem {
  id: string;
  quantity: number;
}

export interface UnavailableItem {
  text: string;
  quantity: number;
}

export interface Order {
  items: OrderItem[];
  unavailable: UnavailableItem[];
}

export interface MenuAnswer {
  message: string;
  suggested_ids: string[];
}

export interface AssistantResponse {
  order: Order | null;
  answer: MenuAnswer | null;
}
