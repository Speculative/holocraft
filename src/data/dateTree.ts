import type dayjs from "dayjs";

function* mapIterator<TOldValue, TNewValue>(
  iterator: Iterable<TOldValue>,
  mapper: (value: TOldValue) => TNewValue
) {
  for (const value of iterator) {
    yield mapper(value);
  }
}

type Granularity = dayjs.UnitType;
type DateTreeChild<
  TValue,
  TGranularities extends readonly Granularity[]
> = TGranularities extends [Granularity, ...infer TChildGranularities]
  ? // If there are multiple granularity levels remaining
    TChildGranularities extends [Granularity, ...Granularity[]]
    ? // Recurse with the topmost granularity removed (tree internal nodes)
      DateTree<TValue, TChildGranularities>
    : // At the lowest granularity level,
      TValue[]
  : // You have to pass at least one granularity
    never;

export class DateTree<TValue, TGranularities extends readonly Granularity[]> {
  private children: DateMap<DateTreeChild<TValue, TGranularities>>;

  constructor(
    /**
     * Expected to be sorted by date
     */
    entries: Iterable<[dayjs.Dayjs, TValue]>,
    /**
     * The date granularities for levels of this tree, e.g. ["year", "month", "day"]
     */
    granularities: TGranularities
  ) {
    const [granularity, ...childGranularities] = granularities;

    // Partition entries
    // This is pretty weird. So inserting into the date map automatically partitions, but will lose the original dates.
    // To avoid this, we pack the original date into the value as well. That way, when we get it back out of the map,
    const partitions = new DateMap<[dayjs.Dayjs, TValue][]>([], granularity);
    for (const [date, value] of entries) {
      let bucket: [dayjs.Dayjs, TValue][] = [];
      if (partitions.has(date)) {
        bucket = partitions.get(date)!;
      }
      bucket.push([date, value]);
      partitions.put(date, bucket);
    }

    // Construct child trees from partitions and the next granularity
    if (childGranularities.length > 0) {
      // Create the next level of the tree
      this.children = new DateMap(
        mapIterator(partitions.entries(), ([dateBucket, bucketEntries]) => [
          dateBucket,
          (new DateTree(
            bucketEntries,
            childGranularities
            // TODO: is there some way (type guard?) that we don't have to cast to any
          ) as any) as DateTreeChild<TValue, TGranularities>,
        ]),
        granularity
      );
    } else {
      // This is the bottom of the tree
      this.children = new DateMap(
        mapIterator(partitions.entries(), ([dateBucket, bucketEntries]) => [
          dateBucket,
          bucketEntries.map(([_, value]) => value) as DateTreeChild<
            TValue,
            TGranularities
          >,
        ]),
        granularity
      );
    }
  }

  public get(date: dayjs.Dayjs) {
    return this.children.get(date);
  }

  public keys() {
    return Array.from(this.children.keys());
  }

  public values() {
    return Array.from(this.children.values());
  }

  public entries() {
    return Array.from(this.children.entries());
  }
}

class DateMap<TValue> {
  private granularity: Granularity;
  private innerMap: {
    [granularityKey: number]: TValue;
  };
  private orderedBuckets: dayjs.Dayjs[];

  constructor(
    entries: Iterable<[dayjs.Dayjs, TValue]>,
    granularity: Granularity
  ) {
    this.granularity = granularity;
    this.innerMap = {};
    this.orderedBuckets = [];

    for (const [key, value] of entries) {
      this.innerMap[this.dateKey(key)] = value;
      this.orderedBuckets.push(key.startOf(this.granularity));
    }
  }

  // TODO: this only exists for partition
  // Partition should maybe not be done via DateMap
  public put(key: dayjs.Dayjs, value: TValue) {
    const normalizedKey = this.dateKey(key);
    if (!(normalizedKey in this.innerMap)) {
      this.orderedBuckets.push(key);
    }

    this.innerMap[this.dateKey(key)] = value;
  }

  public has(key: dayjs.Dayjs) {
    return this.dateKey(key) in this.innerMap;
  }

  public get(key: dayjs.Dayjs): TValue | undefined {
    return this.innerMap[this.dateKey(key)];
  }

  public *keys() {
    for (const bucket of this.orderedBuckets) {
      yield bucket;
    }
  }

  public *values() {
    for (const key of this.keys()) {
      yield this.get(key);
    }
  }

  public *entries(): Generator<[dayjs.Dayjs, TValue]> {
    for (const key of this.keys()) {
      yield [key, this.get(key)!];
    }
  }

  private dateKey(date: dayjs.Dayjs) {
    return date.startOf(this.granularity).unix();
  }
}
