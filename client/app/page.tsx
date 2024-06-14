'use client'

import React, { useEffect } from 'react'

import { Header } from '@/components/header'
import { Hero } from '@/components/hero'
import { FileInput } from '@/components/file-input'
import { BorrowingTable } from '@/components/borrowing-table'
import { useFilesStore } from '@/store/files-store'

export default function Home() {
  const { add, filesZus, isLoading } = useFilesStore()

  return (
    <React.Fragment>
      <Header />
      <Hero />

      <div className='w-full flex justify-center items-center flex-col pb-24 space-y-16'>
        <FileInput
          addFiles={add}
          files={filesZus}
          isLoading={isLoading}
        />

        <BorrowingTable />
      </div>
    </React.Fragment>
  )
}
