import array
from machine import mem32
from micropython import const
from uctypes import addressof

# DMA addresses
DMA_BASE = const(0x50000000)
CH0_READ_ADDR = const(DMA_BASE + 0x000)
CH0_WRITE_ADDR = const(DMA_BASE + 0x004)
CH0_TRANS_COUNT = const(DMA_BASE + 0x008)
CH0_CTRL_TRIG = const(DMA_BASE + 0x00c)
CH1_READ_ADDR = const(DMA_BASE + 0x040)
CH1_WRITE_ADDR = const(DMA_BASE + 0x044)
CH1_TRANS_COUNT = const(DMA_BASE + 0x048)
CH1_CTRL_TRIG = const(DMA_BASE + 0x04c)

# PIO addresses
PIO0_BASE = const(0x50200000)
PIO0_TXF0 = const(PIO0_BASE + 0x010)
PIO0_SM0_CLKDIV = const(PIO0_BASE + 0x0c8)

# DMA CSR config
CH0_SNIFF_EN = const(0x0)
CH0_BSWAP = const(0x0)
CH0_IRQ_QUIET = const(0x1)
CH0_TREQ_SEL = const(0x00)
CH0_CHAIN_TO = const(0x1)
CH0_RING_SEL = const(0x0)
CH0_RING_SIZE = const(0x0)
CH0_INCR_WRITE = const(0x0)
CH0_INCR_READ = const(0x1)
CH0_DATA_SIZE = const(0x2)
CH0_HIGH_PRIORITY = const(0x1)
CH0_EN = const(0x1)
CH1_SNIFF_EN = const(0x0)
CH1_BSWAP = const(0x0)
CH1_IRQ_QUIET = const(0x1)
CH1_TREQ_SEL = const(0x3f)
CH1_CHAIN_TO = const(0x0)
CH1_RING_SEL = const(0x0)
CH1_RING_SIZE = const(0x0)
CH1_INCR_WRITE = const(0x0)
CH1_INCR_READ = const(0x0)
CH1_DATA_SIZE = const(0x2)
CH1_HIGH_PRIORITY = const(0x1)
CH1_EN = const(0x1)


def memory_stream(arr, nword):
    """
    Start the DMA stream.

    Chain 0 reads data from the given array and transfers
    32-bit words to the PIO FIFO. Chain 1 restarts chain 0
    on completion.
    """
    # get memory address of input array
    arr_addr = addressof(arr)

    # config channel 0 and 1 CSRs
    ch0_csr = ((CH0_SNIFF_EN << 23) |
               (CH0_BSWAP << 22) |
               (CH0_IRQ_QUIET << 21) |
               (CH0_TREQ_SEL << 15 ) |
               (CH0_CHAIN_TO << 11) |
               (CH0_RING_SEL << 10) |
               (CH0_RING_SIZE << 6) |
               (CH0_INCR_WRITE << 5) |
               (CH0_INCR_READ << 4) |
               (CH0_DATA_SIZE << 2) |
               (CH0_HIGH_PRIORITY << 1) |
               (CH0_EN << 0)
               )
    ch1_csr = ((CH1_SNIFF_EN << 23) |
               (CH1_BSWAP << 22) |
               (CH1_IRQ_QUIET << 21) |
               (CH1_TREQ_SEL << 15 ) |
               (CH1_CHAIN_TO << 11) |
               (CH1_RING_SEL << 10) |
               (CH1_RING_SIZE << 6) |
               (CH1_INCR_WRITE << 5) |
               (CH1_INCR_READ << 4) |
               (CH1_DATA_SIZE << 2) |
               (CH1_HIGH_PRIORITY << 1) |
               (CH1_EN << 0)
               )

    # set up DMA to PIO DMA transfer
    mem32[CH0_READ_ADDR] =  arr_addr
    mem32[CH0_WRITE_ADDR] = PIO0_TXF0
    mem32[CH0_TRANS_COUNT] = nword
    mem32[CH1_READ_ADDR] = arr_addr
    mem32[CH1_WRITE_ADDR] = CH0_READ_ADDR
    mem32[CH1_TRANS_COUNT] = 1

    # trigger DMA channels
    mem32[CH0_CTRL_TRIG] = ch0_csr
    mem32[CH1_CTRL_TRIG] = ch1_csr
