import { create } from "zustand";
import type { PersistStorage } from "zustand/middleware";
import { persist } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

export type PersistConfig = {
	name: string;
	storage?: PersistStorage<unknown>;
	partialize?: <T>(state: T) => object;
	version?: number;
};

export const StoreBuilder = <T>(
	initialState: T,
	persistConfig?: PersistConfig,
) => {
	type StoreState = T;

	// Create store with or without persistence
	const useStore = persistConfig
		? create<StoreState>()(
				persist(
					immer((_set) => ({
						...initialState,
					})),
					{
						name: persistConfig.name,
						storage: persistConfig.storage,
						partialize: persistConfig.partialize as (state: StoreState) => object,
						version: persistConfig.version,
					},
				),
			)
		: create<StoreState>()(
				immer((_set) => ({
					...initialState,
				})),
			);

	const get = () => useStore.getState();
	const set = useStore.setState;
	const subscribe = useStore.subscribe;

	/**
	 * Creates a factory function that exposes all store state and methods.
	 * Facilitates separating actions from the store state, and using the non-reactive get/set isntead of `useStore`, as it needs to be explicity exposed.
	 * @returns {set} The store state setter
	 * @returns {useStore} The store state React hook
	 * @returns {subscribe} The store subscription function
	 * @returns {Object} The store state and methods
	 */
	const createFactory = <S>(
		args: S,
	): (() => T & S & { set: typeof set; subscribe: typeof subscribe }) => {
		return () => {
			return {
				...get(),
				set,
				subscribe,
				...args,
			};
		};
	};
	return { get, set, useStore, subscribe, createFactory };
};
