import docxtractor as dxtr
import sys
import Models.ImportModel as IM

def main():
    # start_index
    start_index = int(sys.argv[1])
    end_index = int(sys.argv[2])

    filepath = "/threaded/analysis_" + str(int(start_index) + 1) + "_" + str(end_index) + ".xlsx"

    print("start_index is", start_index)
    print("end_index is", end_index)
    print("filepath is", filepath)

    org_sheet = IM.scrape6()
    r = org_sheet.rows[start_index:end_index]

    dxtr.extract(r, filepath, start_index)


if __name__ == "__main__":
    main()

