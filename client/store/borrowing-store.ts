import { devtools } from 'zustand/middleware'
import { create } from 'zustand'
import { IVideoBorrowing } from '@/types'

interface BorrowingState {
  videoBorrowings: IVideoBorrowing[]
  addVideoBorrowings: (newBorrowings: IVideoBorrowing[]) => void
}

export const useBorrowingStore = create<BorrowingState>()(
  devtools((set, get) => ({
    videoBorrowings: [],
    addVideoBorrowings: (newBorrowings) =>
      set((state) => ({
        videoBorrowings: [...state.videoBorrowings, ...newBorrowings]
      }))
  }))
)
